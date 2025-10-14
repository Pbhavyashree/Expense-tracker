# 💰 Expense Tracker Web Application

A fully functional multi-user expense tracker web app built with Flask, SQLite3, HTML, and CSS. Track your income and expenses with beautiful charts, categorization, and detailed reporting.

## 🚀 Features

- **👤 User Authentication**: Secure registration and login system
- **🏠 Personal Dashboard**: Overview of total income, expenses, and net balance per user
- **💼 Transaction Management**: Add, edit, and delete income/expense transactions
- **🏷️ Category Management**: Create and manage custom categories per user
- **📊 Filtering & Reports**: Filter transactions by date, type, and category
- **📥 Data Export**: Export filtered data to CSV format
- **📈 Charts & Visualization**: Monthly income vs expense charts
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices
- **🔒 Data Isolation**: Each user has their own separate data

## 📁 Project Structure

```
expense-tracker/
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── database/
│   └── tracker.db        # SQLite database (created automatically)
├── static/
│   ├── css/
│   │   └── style.css     # All styling
│   └── js/
│       └── charts.js     # Chart visualization code
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Dashboard
│   ├── add.html          # Add/Edit transactions
│   ├── categories.html   # Category management
│   └── reports.html      # Reports and filtering
└── README.md
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Step 1: Install Dependencies
```bash
cd expense-tracker
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
python app.py
```

### Step 3: Access the Application
Open your web browser and navigate to:
```
http://localhost:5000
```

## 📊 Database Schema

### Tables

**users** (New!)
- `id` (INTEGER PRIMARY KEY)
- `username` (TEXT UNIQUE) - Unique username
- `email` (TEXT UNIQUE) - User email address
- `password_hash` (TEXT) - Hashed password
- `created_at` (TIMESTAMP) - Account creation date

**transactions**
- `id` (INTEGER PRIMARY KEY)
- `date` (TEXT) - Transaction date
- `amount` (REAL) - Transaction amount
- `type` (TEXT) - 'income' or 'expense'
- `category_id` (INTEGER) - Foreign key to categories
- `description` (TEXT) - Optional description
- `user_id` (INTEGER) - Foreign key to users (New!)

**categories**
- `id` (INTEGER PRIMARY KEY)
- `name` (TEXT) - Category name
- `user_id` (INTEGER) - Foreign key to users (New!)
- UNIQUE(name, user_id) - Categories are unique per user

**budgets** (Optional - for future features)
- `id` (INTEGER PRIMARY KEY)
- `month` (TEXT) - Month for budget
- `category_id` (INTEGER) - Foreign key to categories
- `amount_limit` (REAL) - Budget limit
- `user_id` (INTEGER) - Foreign key to users (New!)

## 🎯 Usage Guide

### Adding Transactions
1. Click "Add Transaction" from the dashboard or navigation
2. Fill in the required fields:
   - **Date**: Transaction date
   - **Amount**: Transaction amount (positive number)
   - **Type**: Income or Expense
   - **Category**: Optional category selection
   - **Description**: Optional description
3. Click "Add Transaction" to save

### Managing Categories
1. Go to "Categories" in the navigation
2. Add new categories using the form at the top
3. Delete categories you no longer need
4. Default categories are provided for common expenses

### Viewing Reports
1. Go to "Reports" in the navigation
2. Use filters to narrow down transactions:
   - **Type**: Income only, Expenses only, or All
   - **Category**: Specific category or All
   - **Month**: Specific month or All
   - **Year**: Specific year or All
3. Export filtered data to CSV for external analysis

### Dashboard Features
- **Summary Cards**: Show total income, expenses, and net balance
- **Monthly Chart**: Visual representation of income vs expenses over time
- **Recent Transactions**: Quick view of latest 10 transactions
- **Quick Actions**: Easy access to common functions

## 📱 Responsive Design

The application is fully responsive and works on:
- **Desktop**: Full features with optimal layout
- **Tablet**: Adapted layout with touch-friendly interface
- **Mobile**: Compact design with essential features

## 🔧 Customization

### Adding New Features
1. **Backend**: Add new routes in `app.py`
2. **Frontend**: Create new templates in `templates/`
3. **Styling**: Modify `static/css/style.css`
4. **JavaScript**: Extend `static/js/charts.js`

### Modifying the Database
1. Add new tables or columns in the `init_db()` function
2. Update routes to handle new data
3. Modify templates to display new information

### Styling Changes
- Colors: Modify CSS custom properties in `style.css`
- Layout: Adjust grid layouts and flexbox configurations
- Typography: Change font families and sizes

## 🚀 Deployment Options

### Local Development
- Run with `python app.py`
- Debug mode enabled by default

### Production Deployment
1. Set `debug=False` in `app.py`
2. Use a production WSGI server like Gunicorn
3. Configure environment variables
4. Set up database backups

### Docker (Optional)
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 📈 Future Enhancements

- **Budget Tracking**: Set and monitor category budgets
- **Recurring Transactions**: Automate regular income/expenses
- **Multi-currency Support**: Handle different currencies
- **Data Import**: Import from bank statements or other apps
- **Advanced Charts**: More visualization options
- **User Authentication**: Multi-user support
- **Mobile App**: Native mobile application
- **API**: RESTful API for external integrations

## 🐛 Troubleshooting

### Common Issues

**Database not found**
- The SQLite database is created automatically on first run
- Check that the `database/` directory exists

**Port already in use**
- Change the port in `app.py`: `app.run(debug=True, port=5001)`

**Styling not loading**
- Ensure static files are served correctly
- Check browser console for 404 errors

**Form validation errors**
- Ensure JavaScript is enabled in browser
- Check console for JavaScript errors

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the code comments
3. Test with sample data
4. Check browser console for errors

---

**Happy Expense Tracking! 💰📊**