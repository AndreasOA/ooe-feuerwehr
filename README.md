# OÖ Feuerwehr Einsatz Tracker

![Header Banner](banner.png)

---

**OÖ Feuerwehr Einsatz Tracker** is an intuitive live emergency tracker for Upper Austria (Oberösterreich, OÖ). It provides real-time insights into ongoing emergency situations, ensuring efficient communication and coordination for those on the ground.

[**Visit the Live Tracker**](https://ooe-feuerwehr.streamlit.app)

---

## 🚀 Features

- **Live Tracking**: Real-time updates on ongoing emergencies.
- **24-hour Stats**: A glance into the recent emergency activities within the last 24 hours.
- **Interactive Maps**: Geographic representation of the active emergencies.
- **Archival Data**: Easily access historical emergency data.
- **Telegram Notifications**: Real-time notifications delivered through the Telegram group.
- **Responsive Layout**: Optimized for both desktop and mobile browsers.

---

## 🖥️ Pages

1. **Live Tracking**: The primary page where you can view all ongoing emergencies in real-time. It showcases statistics of the last 24 hours and lists all active emergencies with their respective details.

2. **Archiv**: An archival data page where past emergencies and their details are listed for easy access and reference.

---

## 📈 Data Visualizations

- **Active Emergencies**: A table listing all active emergencies with details such as type, date, info, firefighting units in action, locality, and district.
- **Emergency Maps**: An interactive map pinpointing the locations of ongoing emergencies, color-coded by type.
- **24-hour Stats**: Metrics showing the number of ongoing emergencies, total emergencies in the past 24 hours, and the most common emergency type during that period.

---

## 📱 Stay Connected

- **Telegram**: Get real-time notifications on your Telegram app. Join our [Telegram Group](https://t.me/ooefeuerwehr).
  
- **Contact**:
  - [Twitter](https://twitter.com/heyandio)
  - [GitHub](https://github.com/AndreasOA)
  - [Website](https://a-o.dev)

---

## 🛠️ Code Overview

The application integrates MongoDB for data persistence and uses Streamlit for web application rendering. The Python backend handles data fetching, processing, and presentation.

- **Database Operations**: The `DbMethods` class provides methods for CRUD operations with MongoDB.
  
- **Data Visualization**:
  - `taskMapPlot`: Creates an interactive map showcasing emergency locations.
  - `activeTaskTable`: Generates an HTML table that lists all active emergencies.

- **Utility Functions**: Helper functions such as `apply_district_abr_full`, `format_city`, and `makeMapsLink` help in data transformation and representation.

For a deep dive, refer to the provided code and the associated module imports.

---

## 📜 License & Credits

This project is open-source and available under the [MIT License](https://github.com/AndreasOA/ooe-feuerwehr-einsatz-tracker/LICENSE).

© 2023 AndreasOA

---