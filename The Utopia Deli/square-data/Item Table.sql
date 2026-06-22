Drop Table IF EXISTS Item
CREATE TABLE Item (
    SquareItemID NVARCHAR(255) NOT NULL,
    UtopiaItemID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    Name NVARCHAR(255),
    Description NVARCHAR(MAX),  -- Handles long descriptions
    Price DECIMAL(10, 2),
    Stock_Quantity INT
   
);
