# 🗂️ MediPlant Database ER Diagram

## Entity Relationship Diagram - MediPlant E-Commerce Platform

### 🏗️ Core System Overview

```mermaid
erDiagram
    %% Core Entities Overview
    USERS {
        int id PK
        varchar name
        varchar email UK
        varchar password_hash
        int role_id FK
        boolean is_active
        boolean is_verified
    }
    
    ROLES {
        int id PK
        enum name "admin,supplier,consumer"
        varchar description
    }
    
    PRODUCTS {
        int id PK
        varchar name
        varchar slug UK
        int category_id FK
        int supplier_id FK
        decimal base_price
        int stock_quantity
        boolean is_active
        decimal rating_average
    }
    
    CATEGORIES {
        int id PK
        varchar name UK
        varchar slug UK
        int parent_id FK
        boolean is_active
    }
    
    ORDERS {
        int id PK
        varchar order_number UK
        int user_id FK
        int supplier_id FK
        enum status "pending,confirmed,shipped,delivered"
        decimal total_amount
        timestamp created_at
    }
    
    ORDER_ITEMS {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        decimal unit_price
        decimal total_price
    }
    
    PRODUCT_REVIEWS {
        int id PK
        int product_id FK
        int user_id FK
        int rating "1-5"
        text comment
        boolean is_verified
    }
    
    %% Core Relationships
    ROLES ||--o{ USERS : has
    USERS ||--o{ PRODUCTS : supplies
    CATEGORIES ||--o{ PRODUCTS : categorizes
    CATEGORIES ||--o{ CATEGORIES : parent
    USERS ||--o{ ORDERS : places
    USERS ||--o{ ORDERS : fulfills
    ORDERS ||--o{ ORDER_ITEMS : contains
    PRODUCTS ||--o{ ORDER_ITEMS : ordered
    PRODUCTS ||--o{ PRODUCT_REVIEWS : reviewed
    USERS ||--o{ PRODUCT_REVIEWS : writes
```

---

### 👥 User Management Module

```mermaid
erDiagram
    USERS {
        int id PK
        varchar name
        varchar email UK
        varchar password_hash
        varchar phone
        int role_id FK
        boolean is_active
        boolean is_verified
        varchar profile_image
    }
    
    ROLES {
        int id PK
        enum name "admin,supplier,consumer"
        varchar description
    }
    
    SUPPLIER_PROFILES {
        int id PK
        int user_id FK
        varchar business_name
        varchar business_license
        boolean is_approved
        decimal rating
        decimal commission_rate
    }
    
    USER_ADDRESSES {
        int id PK
        int user_id FK
        enum type "home,work,other"
        varchar address_line1
        varchar city
        varchar state
        boolean is_default
    }
    
    EMAIL_VERIFICATIONS {
        int id PK
        int user_id FK
        varchar token
        datetime expires_at
        boolean is_used
    }
    
    %% Relationships
    ROLES ||--o{ USERS : has
    USERS ||--o| SUPPLIER_PROFILES : extends
    USERS ||--o{ USER_ADDRESSES : has
    USERS ||--o{ EMAIL_VERIFICATIONS : verifies
```

---

### 🛍️ Product Catalog Module

```mermaid
erDiagram
    PRODUCTS {
        int id PK
        varchar name
        varchar slug UK
        int category_id FK
        int supplier_id FK
        varchar sku UK
        text description
        decimal base_price
        decimal discount_price
        int stock_quantity
        boolean is_active
        boolean is_featured
        decimal rating_average
        int sales_count
    }
    
    CATEGORIES {
        int id PK
        varchar name UK
        varchar slug UK
        text description
        int parent_id FK
        boolean is_active
        int sort_order
    }
    
    PRODUCT_IMAGES {
        int id PK
        int product_id FK
        varchar image_url
        boolean is_primary
        int sort_order
    }
    
    PRODUCT_VARIANTS {
        int id PK
        int product_id FK
        varchar name
        varchar sku UK
        decimal price
        int stock_quantity
        boolean is_active
    }
    
    PRODUCT_ATTRIBUTES {
        int id PK
        int product_id FK
        varchar attribute_name
        varchar attribute_value
    }
    
    %% Relationships
    CATEGORIES ||--o{ CATEGORIES : parent
    CATEGORIES ||--o{ PRODUCTS : categorizes
    PRODUCTS ||--o{ PRODUCT_IMAGES : has
    PRODUCTS ||--o{ PRODUCT_VARIANTS : has
    PRODUCTS ||--o{ PRODUCT_ATTRIBUTES : has
```

---

### 🛒 Shopping & Order Management

```mermaid
erDiagram
    SHOPPING_CART {
        int id PK
        int user_id FK
        int product_id FK
        int variant_id FK
        int quantity
        timestamp created_at
    }
    
    WISHLISTS {
        int id PK
        int user_id FK
        int product_id FK
        timestamp created_at
    }
    
    ORDERS {
        int id PK
        varchar order_number UK
        int user_id FK
        int supplier_id FK
        enum status "pending,confirmed,processing,shipped,delivered,cancelled"
        enum payment_status "pending,paid,failed,refunded"
        enum payment_method "razorpay,paypal,stripe,cod"
        decimal subtotal
        decimal tax_amount
        decimal shipping_amount
        decimal total_amount
        json shipping_address
        varchar tracking_number
    }
    
    ORDER_ITEMS {
        int id PK
        int order_id FK
        int product_id FK
        int variant_id FK
        int quantity
        decimal unit_price
        decimal total_price
        varchar product_name
    }
    
    COUPONS {
        int id PK
        varchar code UK
        varchar name
        enum discount_type "percentage,fixed"
        decimal discount_value
        decimal minimum_amount
        boolean is_active
        datetime valid_from
        datetime valid_until
    }
    
    ORDER_TRACKING {
        int id PK
        int order_id FK
        varchar status
        text message
        int updated_by FK
        timestamp created_at
    }
    
    %% Relationships
    ORDERS ||--o{ ORDER_ITEMS : contains
    ORDERS ||--o{ ORDER_TRACKING : tracked
    COUPONS ||--o{ ORDERS : applied_to
```

---

### ⭐ Reviews & Communication

```mermaid
erDiagram
    PRODUCT_REVIEWS {
        int id PK
        int product_id FK
        int user_id FK
        int order_id FK
        int rating "1-5"
        varchar title
        text comment
        boolean is_verified
        boolean is_approved
        int helpful_count
    }
    
    REVIEW_HELPFULNESS {
        int id PK
        int review_id FK
        int user_id FK
        boolean is_helpful
    }
    
    CONTACT_MESSAGES {
        int id PK
        varchar name
        varchar email
        varchar subject
        text message
        int user_id FK
        enum status "new,in_progress,resolved,closed"
        int assigned_to FK
    }
    
    MESSAGES {
        int id PK
        int sender_id FK
        int recipient_id FK
        varchar subject
        text message
        boolean is_read
        enum type "general,order_inquiry,product_inquiry,support"
    }
    
    NOTIFICATIONS {
        int id PK
        int user_id FK
        varchar title
        text message
        enum type "order,product,payment,system,promotion"
        boolean is_read
        varchar action_url
    }
    
    %% Relationships
    PRODUCT_REVIEWS ||--o{ REVIEW_HELPFULNESS : voted_on
```

---

### 📊 Analytics & System Management

```mermaid
erDiagram
    PAGE_VIEWS {
        int id PK
        enum page_type "product,category,home,search"
        int page_id
        int user_id FK
        varchar ip_address
        timestamp created_at
    }
    
    SEARCH_QUERIES {
        int id PK
        varchar query
        int user_id FK
        int results_count
        varchar ip_address
        timestamp created_at
    }
    
    SITE_SETTINGS {
        int id PK
        varchar setting_key UK
        text setting_value
        enum setting_type "string,integer,decimal,boolean,json"
        text description
        boolean is_public
    }
    
    AUDIT_LOGS {
        int id PK
        int user_id FK
        varchar action
        varchar table_name
        int record_id
        json old_values
        json new_values
        varchar ip_address
        timestamp created_at
    }
```

---

## � Database Structure Summary

### 🎯 **Modular Design Benefits:**

✅ **Easy to Understand** - Each diagram focuses on specific functionality  
✅ **Clear Relationships** - Simplified connections between related tables  
✅ **Maintainable** - Updates can be made to individual modules  
✅ **Scalable** - New features can be added as separate modules  

### 📊 **Module Overview:**

| Module | Tables | Purpose |
|--------|--------|---------|
| **Core System** | 7 tables | Main entities and relationships |
| **User Management** | 5 tables | Authentication, profiles, addresses |
| **Product Catalog** | 5 tables | Products, categories, variants, images |
| **Shopping & Orders** | 6 tables | Cart, orders, payments, tracking |
| **Reviews & Communication** | 5 tables | Reviews, messages, notifications |
| **Analytics & System** | 4 tables | Analytics, settings, audit logs |

### 🔑 **Key Relationships:**

#### **Core Entity Relationships:**
- `USERS` ↔ `ROLES` (Many-to-One)
- `USERS` → `PRODUCTS` (One-to-Many) *[Supplier relationship]*
- `CATEGORIES` → `PRODUCTS` (One-to-Many)
- `PRODUCTS` → `PRODUCT_VARIANTS` (One-to-Many)
- `ORDERS` → `ORDER_ITEMS` (One-to-Many)

#### **Cross-Module Relationships:**
- `USERS` → `ORDERS` (Customer & Supplier relationships)
- `PRODUCTS` → `ORDER_ITEMS` (Product ordering)
- `USERS` → `PRODUCT_REVIEWS` (Review system)
- `ORDERS` → `PRODUCT_REVIEWS` (Verified purchases)

### 🏗️ **Database Design Principles:**

1. **📱 Modular Architecture** - Logical separation of concerns
2. **🔐 Security First** - Audit trails and user verification
3. **⚡ Performance Optimized** - Strategic indexing and denormalization
4. **🔄 Scalable Design** - Support for growth and new features
5. **🛡️ Data Integrity** - Foreign key constraints and validation

### � **Implementation Notes:**

- **Indexes**: Strategic indexes on frequently queried fields (user_id, product_id, order_id)
- **JSON Fields**: Flexible storage for addresses and audit data
- **Enums**: Constrained values for status fields and categories
- **Timestamps**: Comprehensive tracking of create/update times
- **Soft Deletes**: Use `is_active` flags instead of hard deletes where appropriate

### 🚀 **Development Workflow:**

1. Start with **Core System** module for basic functionality
2. Implement **User Management** for authentication
3. Build **Product Catalog** for inventory management
4. Add **Shopping & Orders** for e-commerce features
5. Integrate **Reviews & Communication** for user engagement
6. Deploy **Analytics & System** for monitoring and insights
