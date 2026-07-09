# Pulse SaaS Analytics Platform

Pulse is an end-to-end SaaS product analytics project designed to demonstrate application development, cloud deployment, relational database integration, and product analytics.

## Project Overview

Pulse simulates a SaaS onboarding platform where users create an account and provide business information.

Registration data is processed by a Python Flask application and stored in a MySQL database hosted on Amazon RDS.

The application is deployed on AWS Elastic Beanstalk.

## Architecture

User Browser
    |
    v
HTML / CSS Frontend
    |
    v
Python Flask Application
    |
    v
AWS Elastic Beanstalk
    |
    v
Amazon RDS MySQL
    |
    v
SQL Analytics
    |
    v
Product Analytics Dashboard

## Current Features

- Multi-step SaaS user registration
- Flask session handling
- Secure password hashing
- Parameterized SQL queries
- MySQL database integration
- Amazon RDS database hosting
- AWS Elastic Beanstalk deployment
- Environment-based configuration
- Application-to-database security group configuration

## Technology Stack

### Backend
- Python
- Flask
- Werkzeug

### Database
- MySQL
- Amazon RDS
- SQL

### Cloud Infrastructure
- AWS Elastic Beanstalk
- Amazon EC2
- AWS IAM
- AWS Security Groups

### Frontend
- HTML
- CSS
- JavaScript

### Development Tools
- Git
- GitHub
- DBeaver
- VS Code

## Cloud Architecture

The Flask application runs inside an AWS Elastic Beanstalk environment.

Elastic Beanstalk provisions and manages the underlying EC2 infrastructure.

The application connects to an Amazon RDS MySQL database using environment variables.

Database access is restricted using AWS Security Groups. The RDS security group allows MySQL traffic on port 3306 from the Elastic Beanstalk EC2 security group.

## Troubleshooting Experience

During deployment, the application encountered HTTP 500 and 504 Gateway Timeout errors.

The issue was traced to database connectivity between the Elastic Beanstalk EC2 instance and Amazon RDS.

The RDS security group initially allowed MySQL traffic only from the developer's local IP address.

The issue was resolved by configuring an inbound MySQL rule on port 3306 that references the Elastic Beanstalk EC2 security group.

## Project Goal

The goal of Pulse is to build an end-to-end product analytics system covering:

Application Data Generation
    |
    v
Cloud Application Deployment
    |
    v
Relational Data Storage
    |
    v
SQL Analytics
    |
    v
Product KPI Development
    |
    v
Interactive Analytics Dashboard

## Planned Analytics Features

- Total registered users
- Active users
- Free vs paid plan distribution
- Users by country
- Users by industry
- Users by company size
- Registration trends
- SaaS conversion metrics
- Interactive product analytics dashboard

## Author

Harshit Tiwari
