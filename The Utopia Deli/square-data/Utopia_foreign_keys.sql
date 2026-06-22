-- Add constraints to Payments table
ALTER TABLE Payments
ADD CONSTRAINT FK_Payments_Order FOREIGN KEY (UtopiaOrderID) REFERENCES [Order](UtopiaOrderID);

ALTER TABLE Payments
ADD CONSTRAINT FK_Payments_Customer FOREIGN KEY (UtopiaID) REFERENCES Customer(UtopiaID);

ALTER TABLE Payments
ADD CONSTRAINT FK_Payments_Item FOREIGN KEY (UtopiaItemID) REFERENCES Item(UtopiaItemID);

-- Add constraints to Order table
ALTER TABLE [Order]
ADD CONSTRAINT FK_Order_Payments FOREIGN KEY (UtopiaPaymentID) REFERENCES Payments(UtopiaPaymentID);

ALTER TABLE [Order]
ADD CONSTRAINT FK_Order_Customer FOREIGN KEY (UtopiaID) REFERENCES Customer(UtopiaID);

ALTER TABLE [Order]
ADD CONSTRAINT FK_Order_Item FOREIGN KEY (UtopiaItemID) REFERENCES Item(UtopiaItemID);
