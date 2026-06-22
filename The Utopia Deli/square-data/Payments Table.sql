drop table if exists Payments;
CREATE TABLE Payments (
    PaymentID NVARCHAR(255) NOT NULL,
    UtopiaPaymentID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    UtopiaOrderID UNIQUEIDENTIFIER,
    UtopiaID INT,
    UtopiaItemID UNIQUEIDENTIFIER NOT NULL,
    Name NVARCHAR(255),
    Description NVARCHAR(MAX),
    Quantity INT DEFAULT 1,
    Price DECIMAL(10, 2),
    Amount DECIMAL(10, 2),
    Status NVARCHAR(50),
    SourceType NVARCHAR(50),
    Created_At DATETIME,
    Refunds NVARCHAR(MAX),
    Disputes NVARCHAR(MAX),
);
