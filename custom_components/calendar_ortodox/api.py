"""API client for Calendar Ortodox."""
from __future__ import annotations

import logging
import re
from datetime import date, datetime
from typing import Any

from aiohttp import ClientSession
from bs4 import BeautifulSoup

from .const import (
    BASE_URL,
    CSS_CLASS_DUMINICA,
    CSS_CLASS_SARBATOARE,
    FEAST_LEVEL_GREAT,
    FEAST_LEVEL_MAJOR,
    FEAST_LEVEL_NORMAL,
)

_LOGGER = logging.getLogger(__name__)

# Romanian month names
MONTHS_RO = {
    1: "ianuarie", 2: "februarie", 3: "martie", 4: "aprilie",
    5: "mai", 6: "iunie", 7: "iulie", 8: "august",
    9: "septembrie", 10: "octombrie", 11: "noiembrie", 12: "decembrie"
}


class OrthodoxCalendarDay:
    """Represents a single day in the Orthodox calendar."""

    def __init__(
        self,
        day: int,
        month: int,
        year: int,
        day_of_week: str,
        saints: str,
        feast_day: bool = False,
        feast_level: str = FEAST_LEVEL_NORMAL,
        fasting_info: list[str] | None = None,
        moon_phase: str | None = None,
        is_sunday: bool = False,
        sunday_title: str | None = None,
        sunday_readings: dict[str, str] | None = None,
    ) -> None:
        """Initialize a calendar day."""
        self.day = day
        self.month = month
        self.year = year
        self.day_of_week = day_of_week
        self.saints = saints
        self.feast_day = feast_day
        self.feast_level = feast_level
        self.fasting_info = fasting_info or []
        self.moon_phase = moon_phase
        self.is_sunday = is_sunday
        self.sunday_title = sunday_title
        self.sunday_readings = sunday_readings or {}

    @property
    def date(self) -> date:
        """Return the date object."""
        return date(self.year, self.month, self.day)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "date": self.date.isoformat(),
            "day_of_week": self.day_of_week,
            "saints": self.saints,
            "feast_day": self.feast_day,
            "feast_level": self.feast_level,
            "fasting_info": self.fasting_info,
            "moon_phase": self.moon_phase,
            "is_sunday": self.is_sunday,
            "sunday_title": self.sunday_title,
            "sunday_readings": self.sunday_readings,
        }


class CalendarOrtodoxAPI:
    """API client for noutati-ortodoxe.ro calendar."""

    def __init__(self, session: ClientSession, year: int | None = None) -> None:
        """Initialize the API client."""
        self._session = session
        self._year = year or datetime.now().year
        self._cache: dict[int, dict[int, list[OrthodoxCalendarDay]]] = {}

    async def get_year_calendar(self, year: int | None = None) -> dict[int, list[OrthodoxCalendarDay]]:
        """Get the full year calendar data."""
        target_year = year or self._year
        
        if target_year in self._cache:
            _LOGGER.debug("Returning cached calendar for year %s", target_year)
            return self._cache[target_year]

        url = BASE_URL
        if target_year != datetime.now().year:
            url = f"{BASE_URL}?year={target_year}"

        _LOGGER.debug("Fetching calendar from %s", url)
        
        try:
            async with self._session.get(url, timeout=30) as response:
                response.raise_for_status()
                html = await response.text()
        except Exception as err:
            _LOGGER.error("Failed to fetch calendar: %s", err)
            raise

        calendar_data = self._parse_calendar_html(html, target_year)
        self._cache[target_year] = calendar_data
        
        return calendar_data

    async def get_month_calendar(self, year: int, month: int) -> list[OrthodoxCalendarDay]:
        """Get calendar data for a specific month."""
        year_calendar = await self.get_year_calendar(year)
        return year_calendar.get(month, [])

    async def get_day_info(self, target_date: date) -> OrthodoxCalendarDay | None:
        """Get calendar info for a specific date."""
        month_calendar = await self.get_month_calendar(target_date.year, target_date.month)
        
        for day_info in month_calendar:
            if day_info.day == target_date.day:
                return day_info
        
        return None

    def _parse_calendar_html(self, html: str, year: int) -> dict[int, list[OrthodoxCalendarDay]]:
        """Parse the HTML calendar and extract data."""
        soup = BeautifulSoup(html, "lxml")
        calendar_data: dict[int, list[OrthodoxCalendarDay]] = {}

        # Find all month calendars
        month_divs = soup.find_all("div", class_="calendar")
        
        for month_idx, month_div in enumerate(month_divs, start=1):
            month_data = []
            
            # Find all day rows (skip header rows)
            rows = month_div.find_all("tr")
            
            for row in rows:
                # Skip if this is the month header row
                if row.find("td", class_="luna"):
                    continue
                
                # Skip if this is a Sunday reading row (duminica)
                if "duminica" in row.get("class", []):
                    # This row contains Sunday readings, we'll handle it separately
                    continue
                
                day_cell = row.find("td", class_="ziua")
                day_of_week_cell = row.find("td", class_="sapt")
                content_cell = row.find("td", recursive=False)  # Third cell
                
                if not day_cell or not day_of_week_cell or not content_cell:
                    continue
                
                try:
                    day_num = int(day_cell.get_text(strip=True))
                except (ValueError, AttributeError):
                    continue
                
                day_of_week = day_of_week_cell.get_text(strip=True)
                
                # Check if it's a feast day (sarbatoare)
                row_classes = row.get("class", [])
                is_feast = CSS_CLASS_SARBATOARE in row_classes
                is_sunday = CSS_CLASS_DUMINICA in row_classes or day_of_week == "D"
                
                # Extract saints and determine feast level
                saints_link = content_cell.find("a", class_="sinaxar")
                if saints_link:
                    saints_text = saints_link.get_text(strip=True)
                    
                    # Determine feast level by counting crosses/daggers
                    feast_level = FEAST_LEVEL_NORMAL
                    if is_feast or "†" in saints_text or "(†)" in saints_text:
                        if "(†)" in saints_text:
                            feast_level = FEAST_LEVEL_GREAT
                        elif "†" in saints_text:
                            feast_level = FEAST_LEVEL_MAJOR
                        is_feast = True
                else:
                    # No sinaxar link - extract text more carefully
                    # First, try to get direct text nodes (excluding spans and other elements)
                    saints_text_parts = []
                    for element in content_cell.children:
                        if isinstance(element, str):
                            text = element.strip()
                            if text:
                                saints_text_parts.append(text)
                        elif element.name == "a":
                            text = element.get_text(strip=True)
                            if text:
                                saints_text_parts.append(text)
                    
                    saints_text = " ".join(saints_text_parts).strip()
                    
                    # If still empty, fall back to getting all text
                    if not saints_text:
                        saints_text = content_cell.get_text(strip=True)
                    
                    feast_level = FEAST_LEVEL_NORMAL
                
                # Extract fasting info from comments
                fasting_info = []
                comment_spans = content_cell.find_all("span", class_="comentariu")
                for comment in comment_spans:
                    comment_text = comment.get_text(strip=True)
                    if any(keyword in comment_text for keyword in ["Post", "Dezlegare", "pâine", "aliturgică"]):
                        fasting_info.append(comment_text)
                
                # Clean up saints_text - remove fasting comments and day numbers
                for fasting in fasting_info:
                    saints_text = saints_text.replace(fasting, "")
                
                # Remove standalone numbers (likely day numbers that got included)
                saints_text = re.sub(r'^\d+\s*', '', saints_text)  # Remove leading numbers
                saints_text = re.sub(r'\s*\d+$', '', saints_text)  # Remove trailing numbers
                saints_text = saints_text.strip()
                
                # If saints_text is empty or just a number, use a placeholder
                if not saints_text or saints_text.isdigit():
                    saints_text = f"Ziua {day_num} {MONTHS_RO[month_idx]}"
                
                # Extract moon phase
                moon_phase = None
                moon_img = content_cell.find("img")
                if moon_img and moon_img.get("src"):
                    moon_src = moon_img["src"]
                    if "luna-" in moon_src:
                        moon_phase = moon_src.split("/")[-1].replace(".png", "")
                
                # Handle Sunday readings (look for next row)
                sunday_title = None
                sunday_readings = {}
                if is_sunday:
                    # Find the next row which should be the duminica row
                    next_row = row.find_next_sibling("tr")
                    if next_row and "duminica" in next_row.get("class", []):
                        title_span = next_row.find("span", class_="title")
                        if title_span:
                            sunday_title = title_span.get_text(strip=True)
                        
                        # Get the full text and parse readings
                        readings_text = next_row.get_text(strip=True)
                        if "Ap." in readings_text:
                            parts = readings_text.split(";")
                            for part in parts:
                                if "Ap." in part:
                                    sunday_readings["apostle"] = part.strip()
                                elif "Ev." in part:
                                    sunday_readings["gospel"] = part.strip()
                
                day_obj = OrthodoxCalendarDay(
                    day=day_num,
                    month=month_idx,
                    year=year,
                    day_of_week=day_of_week,
                    saints=saints_text,
                    feast_day=is_feast,
                    feast_level=feast_level,
                    fasting_info=fasting_info,
                    moon_phase=moon_phase,
                    is_sunday=is_sunday,
                    sunday_title=sunday_title,
                    sunday_readings=sunday_readings,
                )
                
                month_data.append(day_obj)
            
            if month_data:
                calendar_data[month_idx] = month_data
        
        _LOGGER.debug("Parsed %d months of calendar data for year %s", len(calendar_data), year)
        return calendar_data
