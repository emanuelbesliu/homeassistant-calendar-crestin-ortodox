# Calendar Ortodox - Home Assistant Integration

**Integrare custom Home Assistant pentru [calendar creștin ortodox](https://www.noutati-ortodoxe.ro/calendar-ortodox/)**

Monitorizează zilnic sfinții, sărbătorile, posturile și citirile liturgice direct din Home Assistant.

> **Status:** ✅ **v1.0.7 - Stable Release**

---

## ⚠️ DISCLAIMER

**Această integrare utilizează date de la noutati-ortodoxe.ro pentru uz personal și educațional.**

- 📅 Datele calendarului aparțin noutati-ortodoxe.ro
- ⚠️ Integrarea poate **înceta să funcționeze** dacă sursa își schimbă structura
- ⚠️ Utilizarea se face pe **propriul risc**
- 📖 Respectăm conținutul și sursa datelor

**Autorul (Emanuel Besliu) furnizează această integrare "CA ATARE" fără nicio garanție.**

---

## ✨ Caracteristici

### Calendar Entities
- 📅 **Calendar Ortodox Complet** - Toți sfinții și evenimentele zilnice
- ✝️ **Calendar Sărbători** - Doar sărbători majore (marcate cu ✝️ sau 🌟)

### Sensor Entities  
- 🕯️ **Sfântul Zilei** - Informații complete despre ziua curentă
- ⭐ **Următoarea Sărbătoare** - Sărbătoare apropiată cu numărătoare inversă

### Informații Disponibile
- ✝️ **Sfinți zilnici** - Numele sfinților prăznuiți
- 🌟 **Sărbători mari** - Marcate cu cruci (†) și (†)
- 🍞 **Informații despre post** - Tipuri de post și dezlegări
- 📖 **Citiri liturgice** - Apostol și Evanghelie pentru duminici
- 🌙 **Faze lunare** - Informații despre lună
- 📅 **Titluri liturgice** - Duminici și săptămâni speciale

---

## 📦 Instalare

### Metoda 1: HACS (Recomandat)

1. Deschide **HACS** în Home Assistant
2. Mergi la **Integrations**
3. Click pe **⋮** → **Custom repositories**
4. Adaugă URL: `https://github.com/emanuelbesliu/homeassistant-calendar-crestin-ortodox`
5. Categorie: **Integration**
6. Click **Add**
7. Caută "**Calendar Ortodox**" și instalează
8. Restartează Home Assistant

### Metoda 2: Manual

1. Descarcă [ultima versiune](https://github.com/emanuelbesliu/homeassistant-calendar-crestin-ortodox/releases)
2. Copiază folderul `calendar_ortodox` în directorul `custom_components`:
   ```
   /config/custom_components/calendar_ortodox/
   ```
3. Restartează Home Assistant

---

## ⚙️ Configurare

1. Mergi la **Settings** → **Devices & Services** → **Add Integration**
2. Caută "**Calendar Ortodox**"
3. Configurează opțiunile (opțional):
   - **Limba** - Română sau Engleză
   - **Include informații despre post** - Da/Nu
   - **Include citiri liturgice** - Da/Nu
4. Click **Submit**

După câteva secunde, calendarele și senzorii vor apărea!

---

## 📊 Entități Create

### Calendar Entities (2)

| Entity ID | Descriere | Conținut |
|-----------|-----------|----------|
| `calendar.calendar_ortodox` | Calendar complet | Toți sfinții și evenimentele zilnice |
| `calendar.calendar_ortodox_sarbatori` | Doar sărbători | Sărbători majore marcate cu ✝️ și 🌟 |

### Sensor Entities (2)

| Entity ID | Stare | Atribute |
|-----------|-------|----------|
| `sensor.sfantul_zilei` | Sfântul zilei curente | `feast_day`, `feast_level`, `fasting`, `fasting_description`, `moon_phase`, `liturgical_info`, `readings` |
| `sensor.urmatoarea_sarbatoare` | Următoarea sărbătoare | `date`, `days_until`, `feast_level`, `day_of_week` |

---

## 🎯 Înțelegerea Nivelurilor de Sărbătoare

Integrarea recunoaște diferite tipuri de sărbători pe baza marcajelor din calendar:

- **🌟 Praznice Mari** (Great Feasts): Marcate cu `(†)` 
  - Paștile, Crăciunul, Boboteaza, etc.
  - Cele mai importante sărbători creștine

- **✝️ Sărbători** (Major Feasts): Marcate cu `†`
  - Sfinți importanți, soboare, praznice
  - Sărbători cu cruce roșie în calendar

- **Zile Normale**: Fără marcaj special
  - Sfinți zilnici, pomeniri obișnuite

---

## 🍞 Informații despre Post

Integrarea oferă detalii complete despre post:

| Tip Post | Descriere |
|----------|-----------|
| **Post** | Post general |
| **Post negru** | Post strict (doar pâine și apă) |
| **Dezlegare la pește** | Se permite pește |
| **Dezlegare la ulei și vin** | Se permit ulei și vin |
| **Dezlegare la brânză, lapte și ouă** | Se permit produse lactate |
| **Zi aliturgică** | Fără liturghie |

---

## 📈 Exemple de Utilizare

### Automation: Felicitare la Onomastică

```yaml
automation:
  - alias: "Felicitare Onomastică"
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
          message: "Astăzi este Sfântul Ioan! 🎉"
```

### Automation: Notificare Sărbătoare

```yaml
automation:
  - alias: "Anunț Sărbătoare Apropiată"
    trigger:
      - platform: template
        value_template: "{{ state_attr('sensor.urmatoarea_sarbatoare', 'days_until') == 1 }}"
    action:
      - service: notify.all_devices
        data:
          title: "Sărbătoare mâine"
          message: >
            Mâine este {{ states('sensor.urmatoarea_sarbatoare') }}!
```

### Dashboard Card: Sfântul Zilei

```yaml
type: markdown
content: >
  # 🕯️ {{ states('sensor.sfantul_zilei') }}
  
  {% if state_attr('sensor.sfantul_zilei', 'feast_day') %}
  **✝️ Sărbătoare {{ state_attr('sensor.sfantul_zilei', 'feast_level') }}**
  {% endif %}
  
  {% if state_attr('sensor.sfantul_zilei', 'fasting') %}
  **🍞 Post:** {{ state_attr('sensor.sfantul_zilei', 'fasting_description') }}
  {% endif %}
  
  {% if state_attr('sensor.sfantul_zilei', 'liturgical_info') %}
  📖 {{ state_attr('sensor.sfantul_zilei', 'liturgical_info') }}
  {% endif %}
```

### Dashboard Card: Calendar View

```yaml
type: calendar
entities:
  - calendar.calendar_ortodox_sarbatori
title: Sărbători Ortodoxe
```

### Dashboard Card: Următoarea Sărbătoare

```yaml
type: entities
title: Sărbători
entities:
  - entity: sensor.urmatoarea_sarbatoare
    name: Următoarea sărbătoare
    icon: mdi:calendar-star
  - type: attribute
    entity: sensor.urmatoarea_sarbatoare
    attribute: days_until
    name: În
    suffix: zile
  - type: attribute
    entity: sensor.urmatoarea_sarbatoare
    attribute: date
    name: Data
```

---

## 🔄 Actualizare Date

- **Interval implicit:** 6 ore (4 actualizări pe zi)
- **Prima actualizare:** Imediat după configurare
- **Cache:** Datele sunt cache-uite pentru a reduce solicitările

### Serviciu Manual de Reîmprospătare

Poți forța o actualizare imediată a datelor calendarului folosind serviciul:

```yaml
service: calendar_ortodox.refresh_calendar
```

**Utilizări:**
- **Developer Tools:** Settings → Developer Tools → Services → Calendar Ortodox: Refresh calendar
- **Automation:** Adaugă serviciul în automatizările tale
- **Scripts:** Include serviciul în scripturi pentru actualizări la cerere

**Exemplu automation:**
```yaml
automation:
  - alias: "Refresh Calendar Daily"
    trigger:
      - platform: time
        at: "06:00:00"
    action:
      - service: calendar_ortodox.refresh_calendar
```

---

## 📦 Structură Fișiere

```
custom_components/calendar_ortodox/
├── __init__.py          # Setup integrare & coordinator
├── api.py              # Client web scraping
├── calendar.py         # Entități calendar (2)
├── sensor.py           # Entități senzor (2)
├── config_flow.py      # Configurare UI
├── const.py            # Constante
├── manifest.json       # Metadata integrare
├── strings.json        # Traduceri
└── translations/
    ├── en.json         # Engleză
    └── ro.json         # Română
```

---

## 🛠️ Troubleshooting

### Senzorii nu apar

1. Așteaptă 30 secunde după configurare
2. Verifică log-urile: **Settings** → **System** → **Logs**
3. Caută erori cu `calendar_ortodox`
4. Reload integrarea: **Settings** → **Devices & Services** → **Calendar Ortodox** → **Reload**

### Eroare la încărcarea datelor

1. Verifică conexiunea la internet
2. Site-ul noutati-ortodoxe.ro poate fi temporar offline
3. Integrarea va reîncerca automat la următoarea actualizare
4. Forțează o actualizare manuală: `service: calendar_ortodox.refresh_calendar`

### Date lipsă sau incomplete

- Unele zile pot avea mai puține informații
- Citirile liturgice sunt disponibile doar duminica
- Informațiile despre post variază în funcție de perioadă
- **Soluție:** Folosește serviciul `calendar_ortodox.refresh_calendar` pentru a reîmprospăta datele

### Nume sfinți lipsă sau incorecte

Dacă vezi "Ziua X luna" în loc de numele sfântului:
1. Apelează serviciul: `calendar_ortodox.refresh_calendar`
2. Verifică log-urile pentru mesaje de debug
3. Raportează problema pe GitHub Issues cu detalii despre ziua problemă

### Debug

Adaugă în `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.calendar_ortodox: debug
    custom_components.calendar_ortodox.api: debug
```

Apoi restartează Home Assistant și apelează `calendar_ortodox.refresh_calendar` pentru a genera log-uri detaliate.

---

## 🤝 Contribuții

Contribuțiile sunt binevenite!

1. Fork repository-ul
2. Creează un branch: `git checkout -b feature/amazing-feature`
3. Commit: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Deschide un Pull Request

---

## 📝 Licență

MIT License - Copyright (c) 2026 Emanuel Besliu

Vezi [LICENSE](LICENSE) pentru detalii complete.

---

## ⚠️ Disclaimer Legal

Această integrare utilizează date de la noutati-ortodoxe.ro prin web scraping pentru uz personal și educațional. Nu este afiliată, endorsată sau suportată oficial de noutati-ortodoxe.ro.

Utilizarea se face pe propriul risc. Dezvoltatorul nu este responsabil pentru:
- Modificări ale site-ului sursa care pot întrerupe funcționalitatea
- Probleme cauzate de utilizarea incorectă a integrării
- Acuratețea sau completitudinea datelor furnizate

Datele calendarului aparțin noutati-ortodoxe.ro și sunt folosite cu respect pentru conținutul lor religios și educațional.

---

## 📞 Suport

- 🐛 **Bug reports:** [GitHub Issues](https://github.com/emanuelbesliu/homeassistant-calendar-crestin-ortodox/issues)
- 💬 **Discuții:** [GitHub Discussions](https://github.com/emanuelbesliu/homeassistant-calendar-crestin-ortodox/discussions)
- ⭐ **Apreciază proiectul:** [GitHub Stars](https://github.com/emanuelbesliu/homeassistant-calendar-crestin-ortodox)

---

## 🙏 Mulțumiri

- **noutati-ortodoxe.ro** pentru datele calendarului ortodox
- **Comunitatea Home Assistant** pentru documentație și suport
- Toți contribuitorii care îmbunătățesc această integrare

---

**Dezvoltat cu ❤️ și credință de Emanuel Besliu (@emanuelbesliu)**
# Test dependency update
# Test v2
