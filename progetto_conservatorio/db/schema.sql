CREATE TABLE `Materiale` (
  `id_materiale` integer PRIMARY KEY AUTO_INCREMENT,
  `id_editore` integer,
  `id_lingua_testo` integer,
  `id_lingua_originale` integer,
  `titolo` varchar(255) NOT NULL,
  `anno` integer,
  `num_pagine` integer,
  `isbn` varchar(255) UNIQUE,
  `abstract` text,
  `indice` text,
  `tipologia` varchar(255),
  `ebp` varchar(255),
  `livello` varchar(255),
  `link_catalogo` varchar(255)
);

CREATE TABLE `Persona` (
  `id_persona` integer PRIMARY KEY AUTO_INCREMENT,
  `nome` varchar(255),
  `cognome` varchar(255)
);

CREATE TABLE `Editore` (
  `id_editore` integer PRIMARY KEY AUTO_INCREMENT,
  `nome` varchar(255) NOT NULL,
  `citta` varchar(255)
);

CREATE TABLE `Lingua` (
  `id_lingua` integer PRIMARY KEY AUTO_INCREMENT,
  `nome` varchar(255) UNIQUE NOT NULL
);

CREATE TABLE `Categoria` (
  `id_categoria` integer PRIMARY KEY AUTO_INCREMENT,
  `nome` varchar(255) UNIQUE NOT NULL
);

CREATE TABLE `Tag` (
  `id_tag` integer PRIMARY KEY AUTO_INCREMENT,
  `nome` varchar(255) UNIQUE NOT NULL
);

CREATE TABLE `SH` (
  `id_sh` integer PRIMARY KEY AUTO_INCREMENT,
  `termine` varchar(255) UNIQUE NOT NULL
);

CREATE TABLE `Copia` (
  `id_copia` integer PRIMARY KEY AUTO_INCREMENT,
  `numero` varchar(255),
  `collocazione` varchar(255),
  `stato` varchar(255),
  `note` text,
  `nota_critica` text,
  `id_materiale` integer NOT NULL
);

CREATE TABLE `Materiale_Persona` (
  `id_materiale` integer,
  `id_persona` integer,
  `ruolo` varchar(255),
  PRIMARY KEY (`id_materiale`, `id_persona`, `ruolo`)
);

CREATE TABLE `Materiale_Categoria` (
  `id_materiale` integer,
  `id_categoria` integer,
  PRIMARY KEY (`id_materiale`, `id_categoria`)
);

CREATE TABLE `Materiale_Tag` (
  `id_materiale` integer,
  `id_tag` integer,
  PRIMARY KEY (`id_materiale`, `id_tag`)
);

CREATE TABLE `Materiale_SH` (
  `id_materiale` integer,
  `id_sh` integer,
  PRIMARY KEY (`id_materiale`, `id_sh`)
);

ALTER TABLE `Materiale_Persona` ADD FOREIGN KEY (`id_materiale`) REFERENCES `Materiale` (`id_materiale`);

ALTER TABLE `Materiale_Persona` ADD FOREIGN KEY (`id_persona`) REFERENCES `Persona` (`id_persona`);

ALTER TABLE `Materiale_Categoria` ADD FOREIGN KEY (`id_materiale`) REFERENCES `Materiale` (`id_materiale`);

ALTER TABLE `Materiale_Categoria` ADD FOREIGN KEY (`id_categoria`) REFERENCES `Categoria` (`id_categoria`);

ALTER TABLE `Materiale_Tag` ADD FOREIGN KEY (`id_materiale`) REFERENCES `Materiale` (`id_materiale`);

ALTER TABLE `Materiale_Tag` ADD FOREIGN KEY (`id_tag`) REFERENCES `Tag` (`id_tag`);

ALTER TABLE `Copia` ADD FOREIGN KEY (`id_materiale`) REFERENCES `Materiale` (`id_materiale`);

ALTER TABLE `Materiale` ADD FOREIGN KEY (`id_editore`) REFERENCES `Editore` (`id_editore`);

ALTER TABLE `Materiale` ADD FOREIGN KEY (`id_lingua_testo`) REFERENCES `Lingua` (`id_lingua`);

ALTER TABLE `Materiale` ADD FOREIGN KEY (`id_lingua_originale`) REFERENCES `Lingua` (`id_lingua`);

ALTER TABLE `Materiale_SH` ADD FOREIGN KEY (`id_materiale`) REFERENCES `Materiale` (`id_materiale`);

ALTER TABLE `Materiale_SH` ADD FOREIGN KEY (`id_sh`) REFERENCES `SH` (`id_sh`);
