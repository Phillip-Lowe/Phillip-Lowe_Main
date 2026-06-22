-- Re-enable all foreign key constraints
DECLARE @sql NVARCHAR(MAX) = N'';

SELECT @sql += 'ALTER TABLE [' + SCHEMA_NAME(t.schema_id) + '].[' + t.name + '] WITH CHECK CHECK CONSTRAINT [' + fk.name + '];' + CHAR(13)
FROM sys.foreign_keys fk
JOIN sys.tables t ON fk.parent_object_id = t.object_id;

EXEC sp_executesql @sql;
