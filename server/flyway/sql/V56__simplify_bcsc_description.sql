-- Update description for code 'CD'
UPDATE app_fam.fam_user_type_code
SET description = 'BCSC (Dev)'
WHERE user_type_code = 'CD';

-- Update description for code 'CP'
UPDATE app_fam.fam_user_type_code
SET description = 'BCSC'
WHERE user_type_code = 'CP';

-- Update description for code 'CT'
UPDATE app_fam.fam_user_type_code
SET description = 'BCSC (Test)'
WHERE user_type_code = 'CT';
