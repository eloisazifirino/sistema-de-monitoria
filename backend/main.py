from datetime import time
from typing import Literal, Optional

import psycopg2
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel

from database import get_db_connection

app = FastAPI(title="API Sistema de Monitoria", version="1.0.0")

Role = Literal["aluno", "monitor", "professor"]
Modality = Literal["presencial", "online"]
AppointmentStatus = Literal["solicitado", "confirmado", "concluido", "cancelado"]


# ---------------------------------------------------------------- helpers
def internal_error(conn, e: Exception):
    """Desfaz a transação e devolve um erro 500 genérico (sem expor o banco)."""
    conn.rollback()
    print(f"[ERRO] {e}")  # log no servidor
    raise HTTPException(status_code=500, detail="Erro interno do servidor.")


def require_role(cursor, user_id: int, role: str, status_code: int, detail: str):
    cursor.execute("SELECT role FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user or user["role"] != role:
        raise HTTPException(status_code=status_code, detail=detail)


# ------------------------------------------------------------------ login
class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/login", tags=["Autenticação"], summary="Login de usuário")
def login(credentials: LoginRequest):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "SELECT id, name, email, role FROM users WHERE email = %s AND password = %s",
            (credentials.email, credentials.password),
        )
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=401, detail="Email ou senha incorretos")
        return {"message": "Login efetuado com sucesso!", "user": user}
    except HTTPException:
        raise
    except Exception as e:
        internal_error(conn, e)
    finally:
        cursor.close()
        conn.close()


# ------------------------------------------------------------------ users
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: Role


@app.post("/users", status_code=201, tags=["Usuários"], summary="Cadastrar usuário")
def create_user(user: UserCreate):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT id FROM users WHERE email = %s", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Este email já está registado.")

        cursor.execute(
            "INSERT INTO users (name, email, password, role) "
            "VALUES (%s, %s, %s, %s) RETURNING id, name, email, role",
            (user.name, user.email, user.password, user.role),
        )
        new_user = cursor.fetchone()
        conn.commit()
        return {"message": "Utilizador registado com sucesso!", "user": new_user}
    except HTTPException:
        raise
    except Exception as e:
        internal_error(conn, e)
    finally:
        cursor.close()
        conn.close()


# --------------------------------------------------------------- subjects
@app.get("/subjects", tags=["Disciplinas"], summary="Listar disciplinas")
def list_subjects():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT id, name, code FROM subjects")
        return cursor.fetchall()
    except Exception as e:
        internal_error(conn, e)
    finally:
        cursor.close()
        conn.close()


# ------------------------------------------------------------ monitorings
class MonitoringCreate(BaseModel):
    professor_id: int  # quem está executando a ação (validação de permissão)
    subject_id: int
    monitor_id: int
    day: str
    start_time: time
    location: str
    modality: Modality


class MonitoringUpdate(BaseModel):
    professor_id: int
    subject_id: Optional[int] = None
    monitor_id: Optional[int] = None
    day: Optional[str] = None
    start_time: Optional[time] = None
    location: Optional[str] = None
    modality: Optional[Modality] = None


MONITORING_SELECT = """
    SELECT m.id, m.day, m.start_time, m.location, m.modality,
           m.subject_id, m.monitor_id,
           s.name AS subject_name, u.name AS monitor_name
    FROM monitorings m
    JOIN subjects s ON m.subject_id = s.id
    JOIN users u ON m.monitor_id = u.id
"""


@app.post("/monitorings", status_code=201, tags=["Monitorias"], summary="Criar monitoria (professor)")
def create_monitoring(monitoring: MonitoringCreate):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        require_role(cursor, monitoring.professor_id, "professor", 403,
                     "Acesso negado: apenas professores podem registar monitorias.")
        require_role(cursor, monitoring.monitor_id, "monitor", 400,
                     "O utilizador atribuído não existe ou não tem perfil de monitor.")

        cursor.execute("SELECT id FROM subjects WHERE id = %s", (monitoring.subject_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail="A disciplina informada não existe.")

        cursor.execute(
            """
            INSERT INTO monitorings (subject_id, monitor_id, day, start_time, location, modality)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, subject_id, monitor_id, day, start_time, location, modality
            """,
            (monitoring.subject_id, monitoring.monitor_id, monitoring.day,
             monitoring.start_time, monitoring.location, monitoring.modality),
        )
        new_monitoring = cursor.fetchone()
        conn.commit()
        return {"message": "Monitoria registada com sucesso!", "monitoring": new_monitoring}
    except HTTPException:
        raise
    except Exception as e:
        internal_error(conn, e)
    finally:
        cursor.close()
        conn.close()


@app.get("/monitorings", tags=["Monitorias"], summary="Listar monitorias (com filtros)")
def list_monitorings(subject_id: Optional[int] = None, monitor_id: Optional[int] = None,
                     day: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        query = MONITORING_SELECT + " WHERE 1=1"
        params = []
        if subject_id is not None:
            query += " AND m.subject_id = %s"
            params.append(subject_id)
        if monitor_id is not None:
            query += " AND m.monitor_id = %s"
            params.append(monitor_id)
        if day:
            query += " AND m.day ILIKE %s"
            params.append(f"%{day}%")
        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    except Exception as e:
        internal_error(conn, e)
    finally:
        cursor.close()
        conn.close()


@app.get("/monitorings/{monitoring_id}", tags=["Monitorias"], summary="Detalhes de uma monitoria")
def get_monitoring(monitoring_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(MONITORING_SELECT + " WHERE m.id = %s", (monitoring_id,))
        monitoring = cursor.fetchone()
        if not monitoring:
            raise HTTPException(status_code=404, detail="Monitoria não encontrada.")
        return monitoring
    except HTTPException:
        raise
    except Exception as e:
        internal_error(conn, e)
    finally:
        cursor.close()
        conn.close()


@app.put("/monitorings/{monitoring_id}", tags=["Monitorias"], summary="Atualizar monitoria (professor)")
def update_monitoring(monitoring_id: int, data: MonitoringUpdate):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        require_role(cursor, data.professor_id, "professor", 403,
                     "Acesso negado: apenas professores podem editar monitorias.")

        fields = data.model_dump(exclude={"professor_id"}, exclude_none=True)
        if not fields:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar.")

        if "monitor_id" in fields:
            require_role(cursor, fields["monitor_id"], "monitor", 400,
                         "O utilizador atribuído não existe ou não tem perfil de monitor.")
        if "subject_id" in fields:
            cursor.execute("SELECT id FROM subjects WHERE id = %s", (fields["subject_id"],))
            if not cursor.fetchone():
                raise HTTPException(status_code=400, detail="A disciplina informada não existe.")

        # Os nomes das colunas vêm do modelo Pydantic (não do usuário), então é seguro montar o SET.
        set_clause = ", ".join(f"{col} = %s" for col in fields)
        cursor.execute(
            f"UPDATE monitorings SET {set_clause} WHERE id = %s "
            "RETURNING id, subject_id, monitor_id, day, start_time, location, modality",
            (*fields.values(), monitoring_id),
        )
        updated = cursor.fetchone()
        if not updated:
            raise HTTPException(status_code=404, detail="Monitoria não encontrada.")
        conn.commit()
        return {"message": "Monitoria atualizada com sucesso!", "monitoring": updated}
    except HTTPException:
        raise
    except Exception as e:
        internal_error(conn, e)
    finally:
        cursor.close()
        conn.close()


@app.delete("/monitorings/{monitoring_id}", tags=["Monitorias"], summary="Excluir monitoria (professor)")
def delete_monitoring(monitoring_id: int, professor_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        require_role(cursor, professor_id, "professor", 403,
                     "Acesso negado: apenas professores podem excluir monitorias.")

        cursor.execute("DELETE FROM monitorings WHERE id = %s RETURNING id", (monitoring_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Monitoria não encontrada.")
        conn.commit()
        return {"message": "Monitoria excluída com sucesso!"}
    except HTTPException:
        raise
    except psycopg2.errors.ForeignKeyViolation:
        conn.rollback()
        raise HTTPException(
            status_code=409,
            detail="Não é possível excluir: existem agendamentos ou materiais vinculados.",
        )
    except Exception as e:
        internal_error(conn, e)
    finally:
        cursor.close()
        conn.close()


# ----------------------------------------------------------- appointments
class AppointmentCreate(BaseModel):
    student_id: int
    monitoring_id: int
    status: AppointmentStatus = "solicitado"


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


@app.post("/appointments", status_code=201, tags=["Agendamentos"], summary="Agendar atendimento")
def create_appointment(appointment: AppointmentCreate):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        require_role(cursor, appointment.student_id, "aluno", 400,
                     "O utilizador não existe ou não tem perfil de aluno.")

        cursor.execute("SELECT id FROM monitorings WHERE id = %s", (appointment.monitoring_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail="A monitoria informada não existe.")

        cursor.execute(
            "SELECT id FROM appointments WHERE student_id = %s AND monitoring_id = %s "
            "AND status <> 'cancelado'",
            (appointment.student_id, appointment.monitoring_id),
        )
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="Você já possui agendamento nesta monitoria.")

        cursor.execute(
            """
            INSERT INTO appointments (student_id, monitoring_id, status)
            VALUES (%s, %s, %s)
            RETURNING id, student_id, monitoring_id, status, created_at
            """,
            (appointment.student_id, appointment.monitoring_id, appointment.status),
        )
        new_appointment = cursor.fetchone()
        conn.commit()
        return {"message": "Agendamento registado com sucesso!", "appointment": new_appointment}
    except HTTPException:
        raise
    except Exception as e:
        internal_error(conn, e)
    finally:
        cursor.close()
        conn.close()


@app.get("/appointments", tags=["Agendamentos"], summary="Listar agendamentos (histórico / presenças)")
def list_appointments(student_id: Optional[int] = None, monitoring_id: Optional[int] = None):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        query = """
            SELECT a.id AS appointment_id, a.status, a.created_at,
                   m.day, m.start_time, m.location, m.modality,
                   s.name AS subject_name,
                   u.name AS student_name
            FROM appointments a
            JOIN monitorings m ON a.monitoring_id = m.id
            JOIN subjects s ON m.subject_id = s.id
            JOIN users u ON a.student_id = u.id
            WHERE 1=1
        """
        params = []
        if student_id is not None:
            query += " AND a.student_id = %s"
            params.append(student_id)
        if monitoring_id is not None:
            query += " AND a.monitoring_id = %s"
            params.append(monitoring_id)
        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    except Exception as e:
        internal_error(conn, e)
    finally:
        cursor.close()
        conn.close()


@app.put("/appointments/{appointment_id}/status", tags=["Agendamentos"],
         summary="Atualizar status do agendamento")
def update_appointment_status(appointment_id: int, update_data: AppointmentStatusUpdate):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            """
            UPDATE appointments SET status = %s WHERE id = %s
            RETURNING id, student_id, monitoring_id, status, created_at
            """,
            (update_data.status, appointment_id),
        )
        updated = cursor.fetchone()
        if not updated:
            raise HTTPException(status_code=404, detail="Agendamento não encontrado.")
        conn.commit()
        return {"message": "Status do agendamento atualizado com sucesso!", "appointment": updated}
    except HTTPException:
        raise
    except Exception as e:
        internal_error(conn, e)
    finally:
        cursor.close()
        conn.close()


# -------------------------------------------------------------- materials
@app.post("/materials", status_code=201, tags=["Materiais"], summary="Enviar material de estudo")
def create_study_material(
    monitoring_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    file_type: str = Form(...),
    file_attachment: UploadFile = File(...),
):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT id FROM monitorings WHERE id = %s", (monitoring_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail="A monitoria informada não existe.")

        file_data = file_attachment.file.read()

        cursor.execute(
            """
            INSERT INTO study_materials (monitoring_id, title, description, file_type, file_attachment)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, monitoring_id, title, file_type
            """,
            (monitoring_id, title, description, file_type, file_data),
        )
        new_material = cursor.fetchone()
        conn.commit()
        return {"message": "Material de estudo enviado com sucesso!", "material": new_material}
    except HTTPException:
        raise
    except Exception as e:
        internal_error(conn, e)
    finally:
        cursor.close()
        conn.close()