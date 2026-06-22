-- Generate and execute DELETE statements for all user tables
DECLARE @sql NVARCHAR(MAX) = N'';

SELECT @sql += 'DELETE FROM [' + SCHEMA_NAME(schema_id) + '].[' + name + '];' + CHAR(13)
FROM sys.tables
WHERE is_ms_shipped = 0;

EXEC sp_executesql @sql;
