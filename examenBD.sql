USE banco;


CREATE TABLE IF NOT EXISTS Usuarios (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    contraseña_hash VARCHAR(255) NOT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS Cuentas (
    id_cuenta INT PRIMARY KEY AUTO_INCREMENT,
    numero_cuenta VARCHAR(20) UNIQUE NOT NULL,
    saldo DECIMAL(15,2) DEFAULT 0.00,
    estado ENUM('activa', 'bloqueada') DEFAULT 'activa',
    id_usuario INT NOT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario),
    CHECK (saldo >= 0)
);


CREATE TABLE IF NOT EXISTS TiposMovimiento (
    id_tipo_movimiento INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255)
);


CREATE TABLE IF NOT EXISTS Movimientos (
    id_movimiento INT PRIMARY KEY AUTO_INCREMENT,
    id_tipo_movimiento INT NOT NULL,
    monto DECIMAL(15,2) NOT NULL,
    id_cuenta_emisora INT,
    id_cuenta_receptora INT,
    fecha_operacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    nota TEXT,
    FOREIGN KEY (id_tipo_movimiento) REFERENCES TiposMovimiento(id_tipo_movimiento),
    FOREIGN KEY (id_cuenta_emisora) REFERENCES Cuentas(id_cuenta),
    FOREIGN KEY (id_cuenta_receptora) REFERENCES Cuentas(id_cuenta),
    CHECK (monto > 0)
);


INSERT IGNORE INTO TiposMovimiento (id_tipo_movimiento, nombre, descripcion) VALUES
(1, 'APERTURA', 'Apertura de cuenta con saldo inicial'),
(2, 'TRANSFERENCIA_ENTRADA', 'Transferencia recibida'),
(3, 'TRANSFERENCIA_SALIDA', 'Transferencia enviada');



DROP PROCEDURE IF EXISTS sp_RegistrarUsuario;
DELIMITER //
CREATE PROCEDURE sp_RegistrarUsuario(
    IN p_email VARCHAR(255),
    IN p_nombre VARCHAR(100),
    IN p_apellidos VARCHAR(100),
    IN p_contrasena_plana VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;
    
    START TRANSACTION;
    
    IF EXISTS (SELECT 1 FROM Usuarios WHERE email = p_email) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El email ya está registrado';
    END IF;
    
    INSERT INTO Usuarios (email, nombre, apellidos, contraseña_hash)
    VALUES (p_email, p_nombre, p_apellidos, SHA2(p_contrasena_plana, 256));
    
    COMMIT;
END //

DROP PROCEDURE IF EXISTS sp_AbrirCuenta;
CREATE PROCEDURE sp_AbrirCuenta(
    IN p_id_usuario INT,
    IN p_saldo_inicial DECIMAL(15,2)
)
BEGIN
    DECLARE v_numero_cuenta VARCHAR(20);
    DECLARE v_id_cuenta_nueva INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;
    
    START TRANSACTION;
    
    IF p_saldo_inicial < 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El saldo inicial no puede ser negativo';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM Usuarios WHERE id_usuario = p_id_usuario) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El usuario no existe';
    END IF;
    
    SET v_numero_cuenta = CONCAT('CTA', LPAD(FLOOR(RAND() * 1000000000), 9, '0'));
    
    WHILE EXISTS (SELECT 1 FROM Cuentas WHERE numero_cuenta = v_numero_cuenta) DO
        SET v_numero_cuenta = CONCAT('CTA', LPAD(FLOOR(RAND() * 1000000000), 9, '0'));
    END WHILE;
    
    INSERT INTO Cuentas (numero_cuenta, saldo, id_usuario)
    VALUES (v_numero_cuenta, p_saldo_inicial, p_id_usuario);
    
    SET v_id_cuenta_nueva = LAST_INSERT_ID();
    
    IF p_saldo_inicial > 0 THEN
        INSERT INTO Movimientos (id_tipo_movimiento, monto, id_cuenta_receptora, nota)
        VALUES (1, p_saldo_inicial, v_id_cuenta_nueva, 'Apertura de cuenta con saldo inicial');
    END IF;
    
    COMMIT;
END //

DROP PROCEDURE IF EXISTS sp_TransferirDinero;
CREATE PROCEDURE sp_TransferirDinero(
    IN p_id_cuenta_emisora INT,
    IN p_numero_cuenta_receptora VARCHAR(20),
    IN p_monto DECIMAL(15,2),
    IN p_nota TEXT
)
BEGIN
    DECLARE v_saldo_emisor DECIMAL(15,2);
    DECLARE v_estado_emisor VARCHAR(20);
    DECLARE v_estado_receptor VARCHAR(20);
    DECLARE v_id_cuenta_receptora INT;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;
    
    START TRANSACTION;
    
    IF p_monto <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El monto debe ser mayor a cero';
    END IF;
    
    SELECT saldo, estado INTO v_saldo_emisor, v_estado_emisor 
    FROM Cuentas WHERE id_cuenta = p_id_cuenta_emisora FOR UPDATE;
    
    IF v_saldo_emisor IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cuenta emisora no encontrada';
    END IF;
    
    IF v_estado_emisor != 'activa' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cuenta emisora no está activa';
    END IF;
    
    SELECT id_cuenta, estado INTO v_id_cuenta_receptora, v_estado_receptor 
    FROM Cuentas WHERE numero_cuenta = p_numero_cuenta_receptora FOR UPDATE;
    
    IF v_id_cuenta_receptora IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cuenta receptora no encontrada';
    END IF;
    
    IF v_estado_receptor != 'activa' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cuenta receptora no está activa';
    END IF;
    
    IF p_id_cuenta_emisora = v_id_cuenta_receptora THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede transferir a la misma cuenta';
    END IF;
    
    IF v_saldo_emisor < p_monto THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Saldo insuficiente';
    END IF;
    
    -- transferencia
    UPDATE Cuentas SET saldo = saldo - p_monto WHERE id_cuenta = p_id_cuenta_emisora;
    UPDATE Cuentas SET saldo = saldo + p_monto WHERE id_cuenta = v_id_cuenta_receptora;
    
    -- movimientos
    INSERT INTO Movimientos (id_tipo_movimiento, monto, id_cuenta_emisora, id_cuenta_receptora, nota)
    VALUES (3, p_monto, p_id_cuenta_emisora, v_id_cuenta_receptora, p_nota);
    
    INSERT INTO Movimientos (id_tipo_movimiento, monto, id_cuenta_emisora, id_cuenta_receptora, nota)
    VALUES (2, p_monto, p_id_cuenta_emisora, v_id_cuenta_receptora, p_nota);
    
    COMMIT;
END //

DELIMITER ;