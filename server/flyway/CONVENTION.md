# Database Convention

Convention for flyway database migration

## Type or Type Code

-   Use **'UPPER'** case for code value. e.g., USER_TYPE_CODE = **'B'** --> for BCeID user type

## Application Role

-   Prepend application acronym **'[APP_ ]'** for ROLE_NAME value.

    e.g., ROLE_NAME for application FOM: **'FOM_REVIEWER'**

-   Role naming (**DISPLAY_NAME**), please follow: [Best practices for role naming in RBAC applications](https://apps.nrs.gov.bc.ca/int/confluence/display/FSAST1/Best+practices+for+role+naming+in+RBAC+applications?)

## Date or Timestamp

-   Date: **YYYY-MM-DD**
-   Timestamp: use **"timestamp with time zone" (or UTC offset)** for data-type.

    e.g., value could be: **'2025-04-11 20:29:02.329354+00'**
