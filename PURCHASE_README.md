# ERPNext v15 Purchase Customizations

## Overview

This module extends the Cashier Counter app to include comprehensive purchase management customizations for ERPNext v15. The implementation provides advanced discount management, promotional campaigns, turnover incentives, and enhanced purchase workflows.

## Features

### 1. Advanced Discount System

#### Item-wise Discounts
- Supplier-specific item discounts through Purchase Discount Agreement
- Automatic application based on predefined rules
- Minimum quantity requirements support

#### Invoice-wise Discounts
- Supplier default discounts applied at document level
- Configurable discount percentages per supplier
- Real-time calculation and display

#### Seasonal Promotions
- Time-based promotional campaigns
- Item and supplier filtering options
- Automatic activation and deactivation
- Maximum discount amount caps

#### Turnover Incentives
- Volume-based rewards calculated automatically
- Configurable thresholds and percentages
- Yearly, quarterly, and monthly calculation periods
- Maximum incentive amount limits

### 2. Purchase Estimate Management

#### Complete Lifecycle
- Draft → Submit → Convert to Invoice workflow
- Intelligent conversion preserving discount settings
- Status tracking and audit trail

#### Advanced Features
- Copy estimate functionality
- Supplier quotation integration
- Print preview and customization
- Terms and conditions management

### 3. Manager Portal & Analytics

#### Purchase Analytics Dashboard
- Real-time purchase metrics
- Discount utilization reports
- Supplier performance analysis
- Promotional campaign effectiveness

#### Custom Reports
- Purchase Discount Analysis
- Supplier Performance Report
- Promotional Campaign Report
- Turnover Incentive Tracking

### 4. Automation & Scheduling

#### Daily Tasks
- Credit note reminders
- Promotion status updates
- Performance monitoring

#### Weekly Tasks
- Turnover incentive calculations
- Supplier performance analysis
- Data cleanup operations

## Technical Architecture

### Module Structure
```
purchase/
├── doctype/
│   ├── purchase_estimate/
│   ├── purchase_estimate_item/
│   ├── seasonal_promotion/
│   ├── seasonal_promotion_item/
│   ├── seasonal_promotion_supplier/
│   ├── turnover_incentive/
│   └── purchase_discount_agreement/
├── page/
│   └── purchase_analytics/
├── report/
│   └── purchase_discount_analysis/
├── config/
│   └── desktop.py
├── discount_calculations.py
├── tasks.py
└── setup_custom_fields.py
```

### Custom Fields Added

#### Purchase Invoice
- `purchase_type`: Purchase Invoice/Purchase Estimate
- `apply_discount`: Enable discount functionality
- `discount_type`: Item-wise/Invoice-wise
- `total_discount_amount`: Calculated total discount
- `effective_discount_percentage`: Overall discount rate
- `turnover_incentive`: Volume-based incentive amount
- `purchase_estimate_ref`: Reference to converted estimate

#### Purchase Invoice Item
- `discount_percentage`: Item-level discount rate
- `discount_amount`: Calculated discount amount
- `promotion_applied`: Applied promotional campaign name

#### Supplier
- `default_invoice_discount`: Default discount percentage
- `credit_limit`: Maximum credit allowed
- `payment_terms_template`: Default payment terms

#### Item
- `allow_seasonal_discount`: Enable seasonal promotions
- `max_discount_percentage`: Maximum allowed discount

### Business Logic Components

#### Discount Calculator (`discount_calculations.py`)
- Main class for handling all discount calculations
- Supports multiple discount types simultaneously
- Intelligent promotion application
- Turnover incentive calculations

#### Scheduled Tasks (`tasks.py`)
- Automated reminder system
- Promotion lifecycle management
- Performance analytics generation
- Data maintenance operations

## Installation & Setup

### 1. App Installation
```bash
# Install the app
bench --site [site-name] install-app cashiercounter

# Run migrations
bench --site [site-name] migrate

# Create custom fields
bench --site [site-name] execute cashiercounter.purchase.setup_custom_fields.execute
```

### 2. Permission Setup
The module includes predefined roles and permissions:
- **Purchase Manager**: Full access to all purchase features
- **Purchase User**: Limited access with approval requirements

### 3. Configuration

#### Initial Setup
1. Configure supplier default discounts
2. Set up seasonal promotions
3. Define turnover incentive schemes
4. Create purchase discount agreements

#### Scheduled Tasks
Tasks are automatically configured through hooks.py:
- Daily: Credit note reminders, promotion updates
- Weekly: Turnover incentive calculations

## Usage Guide

### 1. Creating Purchase Estimates

1. Navigate to Purchase > Purchase Estimate
2. Select supplier and add items
3. Enable discount application if needed
4. Submit the estimate
5. Convert to Purchase Invoice when ready

### 2. Setting Up Seasonal Promotions

1. Go to Purchase > Seasonal Promotion
2. Define promotion name and description
3. Set start and end dates
4. Configure discount percentage
5. Add applicable items and suppliers
6. Activate the promotion

### 3. Managing Supplier Discounts

1. Navigate to Purchase > Purchase Discount Agreement
2. Select supplier and item
3. Set discount percentage and minimum quantity
4. Define validity period
5. Activate the agreement

### 4. Viewing Analytics

1. Access Purchase Analytics dashboard
2. View real-time metrics and trends
3. Generate custom reports
4. Monitor promotional effectiveness

## API Reference

### Key Methods

#### Discount Calculations
```python
# Apply all discounts to a purchase document
apply_discounts(doc, method)

# Convert estimate to invoice
convert_estimate_to_invoice(estimate_name)

# Get supplier discounts
get_supplier_discounts(supplier)

# Get active promotions
get_active_promotions()
```

#### Client-side Functions
```javascript
// Calculate all discounts
calculate_all_discounts(frm)

// Apply item-specific discount
apply_item_discount(frm, item)

// Convert estimate to invoice
convert_to_purchase_invoice(frm)

// Show discount breakdown
show_discount_breakdown(frm)
```

## Customization

### Adding New Discount Types

1. Extend the `DiscountCalculator` class
2. Add new calculation method
3. Update client-side scripts
4. Modify form layouts as needed

### Custom Reports

1. Create new report in `purchase/report/`
2. Define columns and filters
3. Implement data retrieval logic
4. Add to module configuration

### Workflow Customization

1. Modify approval thresholds in validation functions
2. Add new status options to doctypes
3. Update client-side state management
4. Configure email notifications

## Troubleshooting

### Common Issues

#### Discounts Not Applying
- Check if `apply_discount` is enabled
- Verify supplier discount agreements are active
- Ensure promotional campaigns are within date range
- Check user permissions for discount application

#### Estimate Conversion Failing
- Validate all required fields are filled
- Check approval workflow status
- Ensure sufficient user permissions
- Verify item availability and pricing

#### Performance Issues
- Clear promotion and discount caches
- Optimize database queries
- Review scheduled task performance
- Check system resource usage

### Debug Mode

Enable debug logging for detailed error information:
```python
frappe.log_error("Debug message", "Purchase Customizations")
```

## Support & Maintenance

### Regular Maintenance
- Monitor scheduled task performance
- Review and archive old promotional data
- Update supplier discount agreements
- Validate system performance metrics

### Updates & Patches
- Regular app updates through bench
- Database migrations as needed
- Configuration updates for new features
- Security patches and improvements

## Contributing

To contribute to this module:
1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request
5. Follow ERPNext coding standards

## License

This module is licensed under MIT License. See LICENSE file for details.

## Changelog

### Version 1.0.0 (Current)
- Initial implementation of purchase customizations
- Advanced discount management system
- Purchase estimate functionality
- Manager portal and analytics
- Automated task scheduling
- Custom field integration
- Comprehensive documentation

---

*For technical support, please contact the development team or raise an issue in the repository.*