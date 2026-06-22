-- Drop FKs from Payments
IF EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Payments_Order')
    ALTER TABLE Payments DROP CONSTRAINT FK_Payments_Order;

IF EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Payments_Customer')
    ALTER TABLE Payments DROP CONSTRAINT FK_Payments_Customer;

IF EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Payments_Item')
    ALTER TABLE Payments DROP CONSTRAINT FK_Payments_Item;

-- Drop FKs from [Order]
IF EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Order_Payments')
    ALTER TABLE [Order] DROP CONSTRAINT FK_Order_Payments;

IF EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Order_Customer')
    ALTER TABLE [Order] DROP CONSTRAINT FK_Order_Customer;

IF EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Order_Item')
    ALTER TABLE [Order] DROP CONSTRAINT FK_Order_Item;
