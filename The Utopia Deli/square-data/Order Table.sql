drop table  IF EXISTS [Order]
;
CREATE TABLE[Order] (
    OrderID NVARCHAR(255) NOT NULL,
    UtopiaOrderID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    UtopiaPaymentID UNIQUEIDENTIFIER NULL,  -- Made NULLable to fix insert order issues
    UtopiaID INT,
    UtopiaItemID UNIQUEIDENTIFIER NOT NULL,
    Quantity INT,
    Price DECIMAL(10, 2),
    Name NVARCHAR(255),
    Description NVARCHAR(255)
    
);
