Drop table If Exists Customer;
CREATE TABLE Customer (
    SquareCustomerID NVARCHAR(255) NOT NULL,
    UtopiaID INT NOT NULL PRIMARY KEY IDENTITY(1,1),
    Name NVARCHAR(255) NOT NULL,
    Email NVARCHAR(255),
    Phone NVARCHAR(255),
    Anonymous BIT NOT NULL DEFAULT 0
);
