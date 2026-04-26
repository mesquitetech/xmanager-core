# Site API Routers Documentation

This directory contains three different router implementations for site management, each serving specific purposes and use cases.

## Router Files Overview

### `router.py` - Standard API with Pagination
**Purpose**: Main API with structured responses and advanced query capabilities
**Use Case**: Primary frontend data consumption with pagination and filtering

**Key Features:**
- Pydantic schemas for request/response validation
- Pagination support (`page`, `size` parameters)
- Advanced filtering (search, type, status)
- Structured JSON responses
- Error handling with proper HTTP status codes

**Endpoints:**
- `GET /api/sites/` - Paginated site list with filters
- `GET /api/sites/simple` - Simple site list for dropdowns

**Frontend Usage:** Limited - mainly for structured data queries

---

### `router_complete.py` - Full Featured API
**Purpose**: Complete site management with all business logic and relationships
**Use Case**: Primary frontend operations requiring full site data

**Key Features:**
- Complete CRUD operations with full site data
- Legal information management (landlord, contracts)
- Geospatial coordinate handling
- Custom site fields (rb_type, height, area_type)
- Complex validation and business rules
- Relationship management (legal_info associations)

**Endpoints:**
- `POST /api/sites/nuevo/create` - Create sites with full data
- `PUT /api/sites/nuevo/update/{id}` - Update sites with relationships
- `GET /api/sites/nuevo/list` - Full site listings
- `GET /api/sites/nuevo/detail/{id}` - Complete site details
- `DELETE /api/sites/nuevo/delete/{id}` - Site deletion

**Frontend Usage:** Primary - used by site forms, maps, towers list, finance modules

---

### `router_simple.py` - Basic CRUD API
**Purpose**: Simplified operations for specific use cases and integrations
**Use Case**: Basic site management without complex relationships

**Key Features:**
- Lightweight CRUD operations
- Flexible data input (Dict-based)
- Minimal validation requirements
- Basic coordinate handling
- Simple response format
- Development and testing friendly

**Endpoints:**
- `POST /api/sites/simple/` - Simple site creation
- `PUT /api/sites/simple/{id}` - Basic site updates
- `GET /api/sites/simple/` - All sites list
- `GET /api/sites/simple/{id}` - Single site details
- `DELETE /api/sites/simple/{id}` - Site deletion

**Frontend Usage:** Specific modules - `maintenance.js` uses `/api/sites/simple` for site selection dropdowns

## Architecture Decision

The three-router approach provides:

1. **Separation of Concerns**: Each router handles different complexity levels
2. **Backward Compatibility**: Existing integrations remain functional
3. **Flexibility**: Different frontend modules can use appropriate APIs
4. **Maintainability**: Isolated code for different use cases

## Usage Guidelines

- Use `router.py` for paginated lists and structured queries
- Use `router_complete.py` for full site management operations
- Use `router_simple.py` for basic integrations and specific modules

All routers maintain the same authentication and authorization patterns through JWT tokens.