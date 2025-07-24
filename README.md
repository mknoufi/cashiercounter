# Cashier Counter

Custom cashier module for ERPNext with advanced purchase management capabilities.

## Features

### Cashier Module
- Custom dashboard for cashier collection reporting
- Payment collection and reconciliation
- Transaction monitoring and analytics

### Purchase Customizations (ERPNext v15)
- **Advanced Discount Management**: Item-wise, Invoice-wise, Seasonal, and Turnover-based discounts
- **Purchase Estimate System**: Complete estimate to invoice conversion workflow
- **Promotional Campaigns**: Time-based seasonal promotions with automated application
- **Supplier Management**: Enhanced supplier profiles with discount agreements
- **Manager Portal**: Comprehensive analytics and reporting dashboard
- **Automation**: Scheduled tasks for reminders and incentive calculations

## Installation

```bash
# Install the app
bench get-app https://github.com/mknoufi/cashiercounter
bench --site [site-name] install-app cashiercounter

# Run migrations
bench --site [site-name] migrate

# Set up custom fields for purchase module
bench --site [site-name] execute cashiercounter.purchase.setup_custom_fields.execute
```

## Quick Start

### Purchase Management
1. Set up supplier discount agreements
2. Create seasonal promotions
3. Configure turnover incentive schemes
4. Start creating purchase estimates
5. Access analytics through Purchase Analytics dashboard

### Cashier Operations
1. Access the Cashier Collection Dashboard
2. Monitor payment collections
3. Generate reconciliation reports

## Documentation

- [Purchase Customizations Guide](PURCHASE_README.md) - Detailed documentation for purchase features
- [API Reference](docs/api.md) - Developer documentation
- [User Manual](docs/user-guide.md) - End-user instructions

## Support

For technical support and feature requests, please contact the development team or raise an issue in the repository.
