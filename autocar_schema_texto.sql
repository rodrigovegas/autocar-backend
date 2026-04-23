--
-- PostgreSQL database dump
--

\restrict J1VusnjLTPIdZLdn1nR2DAs7yOilMEgKlZVDmd9ggG8lIryygjWzK6c6lAvQ8P1

-- Dumped from database version 17.9
-- Dumped by pg_dump version 17.9

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

-- *not* creating schema, since initdb creates it


--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA public IS '';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: administrador; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.administrador (
    id uuid NOT NULL,
    firebase_uid character varying(128) NOT NULL,
    nombre_completo character varying(150) NOT NULL,
    correo character varying(150) NOT NULL,
    fecha_registro timestamp with time zone DEFAULT now()
);


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: contenido_educativo; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.contenido_educativo (
    id uuid NOT NULL,
    taller_id uuid NOT NULL,
    titulo character varying(200) NOT NULL,
    cuerpo text NOT NULL,
    categoria character varying(100) NOT NULL,
    url_imagen character varying(500),
    url_video character varying(500),
    estado character varying(20) NOT NULL,
    informe_ia text,
    motivo_rechazo text,
    fecha_publicacion timestamp with time zone DEFAULT now(),
    fecha_revision timestamp with time zone
);


--
-- Name: disponibilidad_taller; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.disponibilidad_taller (
    id uuid NOT NULL,
    taller_id uuid NOT NULL,
    fecha date NOT NULL,
    hora_inicio time without time zone NOT NULL,
    hora_fin time without time zone NOT NULL,
    cupos_totales smallint NOT NULL,
    cupos_ocupados smallint NOT NULL,
    activo boolean NOT NULL
);


--
-- Name: especialidad; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.especialidad (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    nombre character varying(100) NOT NULL,
    activo boolean DEFAULT true NOT NULL
);


--
-- Name: mantenimiento; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.mantenimiento (
    id uuid NOT NULL,
    reserva_id uuid NOT NULL,
    vehiculo_id uuid NOT NULL,
    taller_id uuid NOT NULL,
    kilometraje_registro integer NOT NULL,
    observaciones text,
    fecha_realizado date NOT NULL,
    fecha_registro timestamp with time zone DEFAULT now(),
    costo numeric(10,2),
    detalle_tecnico text,
    problemas_detectados text,
    gravedad_problemas character varying(10),
    km_proximo_mantenimiento integer,
    fecha_proximo_mantenimiento date,
    recomendaciones text
);


--
-- Name: notificacion; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notificacion (
    id uuid NOT NULL,
    destinatario_tipo character varying(20) NOT NULL,
    destinatario_id uuid NOT NULL,
    titulo character varying(150) NOT NULL,
    mensaje text NOT NULL,
    tipo character varying(50) NOT NULL,
    leida boolean NOT NULL,
    fecha_envio timestamp with time zone DEFAULT now()
);


--
-- Name: recordatorio; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.recordatorio (
    id uuid NOT NULL,
    usuario_id uuid NOT NULL,
    vehiculo_id uuid NOT NULL,
    tipo_mantenimiento_id uuid NOT NULL,
    origen character varying(20) NOT NULL,
    fecha_programada date,
    kilometraje_programado integer,
    texto_personalizado text,
    estado character varying(20) NOT NULL,
    fecha_creacion timestamp with time zone DEFAULT now(),
    fecha_envio timestamp with time zone
);


--
-- Name: reserva; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.reserva (
    id uuid NOT NULL,
    usuario_id uuid NOT NULL,
    taller_id uuid NOT NULL,
    vehiculo_id uuid NOT NULL,
    disponibilidad_id uuid NOT NULL,
    estado character varying(20) NOT NULL,
    motivo_rechazo text,
    fecha_creacion timestamp with time zone DEFAULT now(),
    fecha_actualizacion timestamp with time zone DEFAULT now(),
    descripcion_otro text,
    calificacion smallint,
    comentario_calificacion text,
    CONSTRAINT reserva_calificacion_check CHECK (((calificacion >= 1) AND (calificacion <= 5)))
);


--
-- Name: reserva_servicio; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.reserva_servicio (
    id uuid NOT NULL,
    reserva_id uuid NOT NULL,
    servicio_taller_id uuid NOT NULL
);


--
-- Name: servicio_taller; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.servicio_taller (
    id uuid NOT NULL,
    taller_id uuid NOT NULL,
    tipo_mantenimiento_id uuid NOT NULL,
    nombre_personalizado character varying(100),
    descripcion_personalizada text,
    tiempo_estimado_minutos smallint NOT NULL,
    activo boolean NOT NULL
);


--
-- Name: taller; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.taller (
    id uuid NOT NULL,
    firebase_uid character varying(128) NOT NULL,
    nombre character varying(150) NOT NULL,
    direccion_texto character varying(250) NOT NULL,
    telefono character varying(20) NOT NULL,
    correo character varying(150) NOT NULL,
    latitud numeric(10,7),
    longitud numeric(10,7),
    estado character varying(20) NOT NULL,
    fecha_registro timestamp with time zone DEFAULT now(),
    fecha_activacion timestamp with time zone,
    especialidad_id uuid NOT NULL
);


--
-- Name: tipo_mantenimiento; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tipo_mantenimiento (
    id uuid NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion_base text NOT NULL,
    intervalo_km integer,
    intervalo_dias integer,
    activo boolean NOT NULL,
    estado character varying(20) DEFAULT 'aprobado'::character varying NOT NULL
);


--
-- Name: usuario; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.usuario (
    id uuid NOT NULL,
    firebase_uid character varying(128) NOT NULL,
    nombre_completo character varying(150) NOT NULL,
    correo character varying(150) NOT NULL,
    telefono character varying(20),
    fecha_registro timestamp with time zone DEFAULT now(),
    activo boolean NOT NULL
);


--
-- Name: vehiculo; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vehiculo (
    id uuid NOT NULL,
    usuario_id uuid NOT NULL,
    marca character varying(80) NOT NULL,
    modelo character varying(80) NOT NULL,
    anio smallint NOT NULL,
    kilometraje_actual integer NOT NULL,
    fecha_registro timestamp with time zone DEFAULT now(),
    activo boolean NOT NULL,
    placa character varying(10),
    color character varying(50),
    tipo_combustible character varying(20)
);


--
-- Name: administrador administrador_correo_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.administrador
    ADD CONSTRAINT administrador_correo_key UNIQUE (correo);


--
-- Name: administrador administrador_firebase_uid_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.administrador
    ADD CONSTRAINT administrador_firebase_uid_key UNIQUE (firebase_uid);


--
-- Name: administrador administrador_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.administrador
    ADD CONSTRAINT administrador_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: contenido_educativo contenido_educativo_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contenido_educativo
    ADD CONSTRAINT contenido_educativo_pkey PRIMARY KEY (id);


--
-- Name: disponibilidad_taller disponibilidad_taller_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.disponibilidad_taller
    ADD CONSTRAINT disponibilidad_taller_pkey PRIMARY KEY (id);


--
-- Name: especialidad especialidad_nombre_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.especialidad
    ADD CONSTRAINT especialidad_nombre_key UNIQUE (nombre);


--
-- Name: especialidad especialidad_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.especialidad
    ADD CONSTRAINT especialidad_pkey PRIMARY KEY (id);


--
-- Name: mantenimiento mantenimiento_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mantenimiento
    ADD CONSTRAINT mantenimiento_pkey PRIMARY KEY (id);


--
-- Name: mantenimiento mantenimiento_reserva_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mantenimiento
    ADD CONSTRAINT mantenimiento_reserva_id_key UNIQUE (reserva_id);


--
-- Name: notificacion notificacion_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notificacion
    ADD CONSTRAINT notificacion_pkey PRIMARY KEY (id);


--
-- Name: recordatorio recordatorio_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recordatorio
    ADD CONSTRAINT recordatorio_pkey PRIMARY KEY (id);


--
-- Name: reserva reserva_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reserva
    ADD CONSTRAINT reserva_pkey PRIMARY KEY (id);


--
-- Name: reserva_servicio reserva_servicio_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reserva_servicio
    ADD CONSTRAINT reserva_servicio_pkey PRIMARY KEY (id);


--
-- Name: servicio_taller servicio_taller_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.servicio_taller
    ADD CONSTRAINT servicio_taller_pkey PRIMARY KEY (id);


--
-- Name: taller taller_correo_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.taller
    ADD CONSTRAINT taller_correo_key UNIQUE (correo);


--
-- Name: taller taller_firebase_uid_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.taller
    ADD CONSTRAINT taller_firebase_uid_key UNIQUE (firebase_uid);


--
-- Name: taller taller_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.taller
    ADD CONSTRAINT taller_pkey PRIMARY KEY (id);


--
-- Name: tipo_mantenimiento tipo_mantenimiento_nombre_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tipo_mantenimiento
    ADD CONSTRAINT tipo_mantenimiento_nombre_key UNIQUE (nombre);


--
-- Name: tipo_mantenimiento tipo_mantenimiento_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tipo_mantenimiento
    ADD CONSTRAINT tipo_mantenimiento_pkey PRIMARY KEY (id);


--
-- Name: disponibilidad_taller uq_disponibilidad; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.disponibilidad_taller
    ADD CONSTRAINT uq_disponibilidad UNIQUE (taller_id, fecha, hora_inicio, hora_fin);


--
-- Name: reserva_servicio uq_reserva_servicio; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reserva_servicio
    ADD CONSTRAINT uq_reserva_servicio UNIQUE (reserva_id, servicio_taller_id);


--
-- Name: servicio_taller uq_taller_tipo; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.servicio_taller
    ADD CONSTRAINT uq_taller_tipo UNIQUE (taller_id, tipo_mantenimiento_id);


--
-- Name: usuario usuario_correo_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_correo_key UNIQUE (correo);


--
-- Name: usuario usuario_firebase_uid_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_firebase_uid_key UNIQUE (firebase_uid);


--
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (id);


--
-- Name: vehiculo vehiculo_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehiculo
    ADD CONSTRAINT vehiculo_pkey PRIMARY KEY (id);


--
-- Name: vehiculo vehiculo_placa_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehiculo
    ADD CONSTRAINT vehiculo_placa_key UNIQUE (placa);


--
-- Name: contenido_educativo contenido_educativo_taller_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contenido_educativo
    ADD CONSTRAINT contenido_educativo_taller_id_fkey FOREIGN KEY (taller_id) REFERENCES public.taller(id);


--
-- Name: disponibilidad_taller disponibilidad_taller_taller_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.disponibilidad_taller
    ADD CONSTRAINT disponibilidad_taller_taller_id_fkey FOREIGN KEY (taller_id) REFERENCES public.taller(id);


--
-- Name: mantenimiento mantenimiento_reserva_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mantenimiento
    ADD CONSTRAINT mantenimiento_reserva_id_fkey FOREIGN KEY (reserva_id) REFERENCES public.reserva(id);


--
-- Name: mantenimiento mantenimiento_taller_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mantenimiento
    ADD CONSTRAINT mantenimiento_taller_id_fkey FOREIGN KEY (taller_id) REFERENCES public.taller(id);


--
-- Name: mantenimiento mantenimiento_vehiculo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mantenimiento
    ADD CONSTRAINT mantenimiento_vehiculo_id_fkey FOREIGN KEY (vehiculo_id) REFERENCES public.vehiculo(id);


--
-- Name: recordatorio recordatorio_tipo_mantenimiento_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recordatorio
    ADD CONSTRAINT recordatorio_tipo_mantenimiento_id_fkey FOREIGN KEY (tipo_mantenimiento_id) REFERENCES public.tipo_mantenimiento(id);


--
-- Name: recordatorio recordatorio_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recordatorio
    ADD CONSTRAINT recordatorio_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuario(id);


--
-- Name: recordatorio recordatorio_vehiculo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recordatorio
    ADD CONSTRAINT recordatorio_vehiculo_id_fkey FOREIGN KEY (vehiculo_id) REFERENCES public.vehiculo(id);


--
-- Name: reserva reserva_disponibilidad_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reserva
    ADD CONSTRAINT reserva_disponibilidad_id_fkey FOREIGN KEY (disponibilidad_id) REFERENCES public.disponibilidad_taller(id);


--
-- Name: reserva_servicio reserva_servicio_reserva_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reserva_servicio
    ADD CONSTRAINT reserva_servicio_reserva_id_fkey FOREIGN KEY (reserva_id) REFERENCES public.reserva(id);


--
-- Name: reserva_servicio reserva_servicio_servicio_taller_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reserva_servicio
    ADD CONSTRAINT reserva_servicio_servicio_taller_id_fkey FOREIGN KEY (servicio_taller_id) REFERENCES public.servicio_taller(id);


--
-- Name: reserva reserva_taller_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reserva
    ADD CONSTRAINT reserva_taller_id_fkey FOREIGN KEY (taller_id) REFERENCES public.taller(id);


--
-- Name: reserva reserva_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reserva
    ADD CONSTRAINT reserva_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuario(id);


--
-- Name: reserva reserva_vehiculo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reserva
    ADD CONSTRAINT reserva_vehiculo_id_fkey FOREIGN KEY (vehiculo_id) REFERENCES public.vehiculo(id);


--
-- Name: servicio_taller servicio_taller_taller_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.servicio_taller
    ADD CONSTRAINT servicio_taller_taller_id_fkey FOREIGN KEY (taller_id) REFERENCES public.taller(id);


--
-- Name: servicio_taller servicio_taller_tipo_mantenimiento_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.servicio_taller
    ADD CONSTRAINT servicio_taller_tipo_mantenimiento_id_fkey FOREIGN KEY (tipo_mantenimiento_id) REFERENCES public.tipo_mantenimiento(id);


--
-- Name: taller taller_especialidad_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.taller
    ADD CONSTRAINT taller_especialidad_id_fkey FOREIGN KEY (especialidad_id) REFERENCES public.especialidad(id);


--
-- Name: vehiculo vehiculo_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehiculo
    ADD CONSTRAINT vehiculo_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuario(id);


--
-- PostgreSQL database dump complete
--

\unrestrict J1VusnjLTPIdZLdn1nR2DAs7yOilMEgKlZVDmd9ggG8lIryygjWzK6c6lAvQ8P1

