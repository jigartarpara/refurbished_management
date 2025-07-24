# Refurbished Business Management System (Built on ERPNext)

## 🚀 Overview

This project is a **customized ERP solution built on top of [ERPNext](https://erpnext.com/)** — a robust open-source ERP platform. Our aim is to provide a **refined, optimized, and industry-specific business management system** for SMEs with enhanced UI/UX, tailored workflows, and extended functionality.

> ✅ Best suited for industries like **textile**, **manufacturing**, **retail**, and **service businesses**.

---

## ✨ What's New in This Refurbished ERP

### ✅ UI/UX Enhancements
- Modern, responsive design (Tailwind CSS)
- Mobile-friendly interfaces
- Custom dashboards for quick insights

### 📦 Industry-Specific Modules
- Textile management extensions (Loom, Yarn, Grey Cloth)
- Manufacturing BOM enhancements
- GST-ready invoicing (India-focused)

### 🔧 Backend Improvements
- Optimized performance and queries
- Custom Doctypes and Scripts
- Advanced Role-Based Permissions (RBAC)

### 📊 Advanced Reporting
- Real-time KPI dashboards
- Custom financial and inventory reports
- Export to Excel, PDF

### 🔗 Integrations
- WhatsApp/SMS Notifications
- Payment Gateway Integration (Razorpay, Stripe)
- E-invoicing & GST Portal Integration (India)

---

## ⚙️ Technology Stack

| Component     | Tool/Framework                         |
|---------------|----------------------------------------|
| Core ERP      | ERPNext (Frappe Framework)             |
| Frontend UI   | Tailwind CSS, Custom JS                |
| Backend       | Python, Frappe                         |
| Database      | MariaDB                                |
| Hosting       | Docker, Nginx, Supervisor, Redis       |
| Deployment    | Self-hosted / Cloud (DigitalOcean, AWS)|

---

## 📦 Installation

### Prerequisites
- Bench CLI (Frappe/ERPNext)
- Docker (optional for containerized setup)
- Node.js, Yarn, Redis, MariaDB

### Clone Repository

# Setup Bench and install dependencies
bench init my-bench --frappe-branch version-15
cd my-bench
bench get-app https://github.com/jigartarpara/refurbished_management.git
bench new-site yoursite.local
bench --site yoursite.local install-app refurbished_management
bench start
