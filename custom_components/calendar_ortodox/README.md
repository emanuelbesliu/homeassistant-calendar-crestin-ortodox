# Calendar Ortodox - Home Assistant Integration

A Home Assistant custom integration that provides Orthodox Christian calendar information from [noutati-ortodoxe.ro](https://www.noutati-ortodoxe.ro/calendar-ortodox/).

> **Current Version:** v1.0.7

## Features

### Calendar Entities
- **Full Orthodox Calendar** - All daily saints and events
- **Feast Days Calendar** (Sărbători) - Major feast days only (marked with ✝️ or 🌟)

### Sensor Entities
- **Sfântul Zilei** (Saint of the Day) - Current day's saints and information
- **Următoarea Sărbătoare** (Next Feast Day) - Upcoming feast day with countdown

### Services
- **refresh_calendar** - Manually force a data refresh from the website

### Information Provided
- ✝️ Daily saints (Sfinți)
- 🌟 Major feast days (Sărbători mari) - marked with crosses (†)
- 🍞 Fasting information (Post)
- 📖 Sunday liturgical readings (Apostle and Gospel)
- 🌙 Moon phases
- 📅 Liturgical titles and descriptions

## Installation

### Manual Installation
1. Copy the `custom_components/calendar_ortodox` directory to your Home Assistant `custom_components` folder
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "Calendar Ortodox" and click to add

### HACS Installation (coming soon)
1. Open HACS in Home Assistant
2. Go to Integrations
3. Click the three dots menu and select "Custom repositories"
4. Add this repository URL
5. Search for "Calendar Ortodox" and install

## Configuration

The integration can be configured via the UI (Settings → Devices & Services).

### Configuration Options
- **Language**: Choose between Romanian (ro) or English (en)
- **Include Fasting Information**: Show/hide fasting details
- **Include Liturgical Readings**: Show/hide Sunday readings

## Entities Created

### Calendar Entities
1. **calendar.calendar_ortodox**
   - Full Orthodox calendar with all saints and events
   - Shows feast days marked with ✝️ (major) or 🌟 (great)
   - Includes fasting information and Sunday readings in descriptions

2. **calendar.calendar_ortodox_sarbatori**
   - Only major feast days (sărbători)
   - Filtered view showing only important celebrations

### Sensor Entities
1. **sensor.sfantul_zilei** (Saint of the Day)
   - State: Current day's saints
   - Attributes:
     - `day_of_week`: Day name (L, M, M, J, V, S, D)
     - `feast_day`: True if it's a feast day
     - `feast_level`: "major", "great", or "normal"
     - `fasting`: True if fasting applies
     - `fasting_description`: Fasting rules for the day
     - `moon_phase`: Current moon phase
     - `liturgical_info`: Sunday title (if applicable)
     - `readings`: Apostle and Gospel readings (if Sunday)

2. **sensor.urmatoarea_sarbatoare** (Next Feast Day)
   - State: Name of next feast day
   - Attributes:
     - `date`: Date of the feast
     - `days_until`: Days until the feast
     - `feast_level`: Level of the feast
     - `day_of_week`: Day name

## Understanding Feast Levels

The integration recognizes different types of feast days based on the markers in the original calendar:

- **🌟 Great Feasts** (Praznice Mari): Marked with `(†)` - Most important celebrations like Paști (Easter), Crăciun (Christmas)
- **✝️ Major Feasts** (Sărbători): Marked with `†` - Important saints and celebrations
- **Regular Days**: No special marking

## Fasting Information

The integration provides detailed fasting information:
- **Post** - General fasting
- **Post negru** - Strict fasting (bread and water only)
- **Dezlegare la pește** - Fish allowed
- **Dezlegare la ulei și vin** - Oil and wine allowed
- **Dezlegare la brânză, lapte și ouă** - Dairy and eggs allowed
- **Zi aliturgică** - No liturgy

## Usage Examples

### Service: Manual Refresh

Force an immediate refresh of calendar data:

```yaml
service: calendar_ortodox.refresh_calendar
```

Use in automations:
```yaml
automation:
  - alias: "Refresh Calendar Every Morning"
    trigger:
      - platform: time
        at: "06:00:00"
    action:
      - service: calendar_ortodox.refresh_calendar
```

### Automation: Birthday Greeting for Name Day
```yaml
automation:
  - alias: "Name Day Greeting"
    trigger:
      - platform: state
        entity_id: sensor.sfantul_zilei
    condition:
      - condition: template
        value_template: "{{ 'Ioan' in states('sensor.sfantul_zilei') }}"
    action:
      - service: notify.mobile_app
        data:
          title: "La mulți ani!"
          message: "Astăzi este Sfântul Ioan!"
```

### Automation: Reminder for Feast Days
```yaml
automation:
  - alias: "Feast Day Reminder"
    trigger:
      - platform: state
        entity_id: sensor.urmatoarea_sarbatoare
    action:
      - service: notify.mobile_app
        data:
          title: "Sărbătoare aproape"
          message: >
            {{ states('sensor.urmatoarea_sarbatoare') }} 
            în {{ state_attr('sensor.urmatoarea_sarbatoare', 'days_until') }} zile
```

### Dashboard Card: Today's Saint
```yaml
type: entities
entities:
  - entity: sensor.sfantul_zilei
    name: Sfântul zilei
    icon: mdi:calendar-star
  - type: attribute
    entity: sensor.sfantul_zilei
    attribute: fasting_description
    name: Post
  - type: attribute
    entity: sensor.sfantul_zilei
    attribute: liturgical_info
    name: Duminica
```

### Dashboard Card: Calendar View
```yaml
type: calendar
entities:
  - calendar.calendar_ortodox_sarbatori
title: Sărbători Ortodoxe
```

## Data Update

The integration updates calendar data every 6 hours. The calendar is cached to reduce load on the source website.

## Technical Details

- **Data Source**: [noutati-ortodoxe.ro](https://www.noutati-ortodoxe.ro/calendar-ortodox/)
- **Update Interval**: 6 hours
- **Platforms**: Calendar, Sensor
- **Dependencies**: BeautifulSoup4, lxml

## Support

For issues, questions, or feature requests, please open an issue on [GitHub](https://github.com/emanuelbesliu/calendar_ortodox).

## Credits

- Calendar data provided by [noutati-ortodoxe.ro](https://www.noutati-ortodoxe.ro)
- Integration developed by @emanuelbesliu

## License

This integration is provided as-is for personal use. The calendar data belongs to noutati-ortodoxe.ro.
