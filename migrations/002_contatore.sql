CREATE TABLE `Contatore` (
  `id` integer PRIMARY KEY,
  `valore` integer NOT NULL DEFAULT 0
);

INSERT INTO `Contatore` (`id`, `valore`) VALUES (1, 0);