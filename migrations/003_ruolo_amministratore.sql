ALTER TABLE `Amministratore`
  ADD COLUMN `ruolo` VARCHAR(50) NOT NULL DEFAULT 'Bibliotecario';


-- UPDATE Amministratore SET ruolo = 'Amministratore' WHERE username = 'username';
