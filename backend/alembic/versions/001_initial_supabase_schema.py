"""001_initial_supabase_schema

Revision ID: 001_initial_supabase
Revises: 
Create Date: 2026-09-29 10:40:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial_supabase'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('candidate_id', sa.String(length=50), nullable=True),
        sa.Column('admin_id', sa.String(length=50), nullable=True),
        sa.Column('full_name', sa.String(length=120), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=True),
        sa.Column('institution', sa.String(length=120), nullable=True),
        sa.Column('phone', sa.String(length=30), nullable=True),
        sa.Column('target_role', sa.String(length=100), nullable=True),
        sa.Column('profile_photo', sa.String(length=255), nullable=True),
        sa.Column('location', sa.String(length=120), nullable=True),
        sa.Column('linkedin', sa.String(length=255), nullable=True),
        sa.Column('github', sa.String(length=255), nullable=True),
        sa.Column('education', sa.Text(), nullable=True),
        sa.Column('experience', sa.Text(), nullable=True),
        sa.Column('email_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('candidate_id'),
        sa.UniqueConstraint('admin_id')
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_candidate_id', 'users', ['candidate_id'])
    op.create_index('ix_users_admin_id', 'users', ['admin_id'])

    # 2. resumes table
    op.create_table(
        'resumes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('raw_text', sa.Text(), nullable=True),
        sa.Column('candidate_name', sa.String(length=120), nullable=True),
        sa.Column('education', sa.Text(), nullable=True),
        sa.Column('experience', sa.Text(), nullable=True),
        sa.Column('technical_skills', sa.Text(), nullable=True),
        sa.Column('soft_skills', sa.Text(), nullable=True),
        sa.Column('screening_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('is_verified', sa.Boolean(), nullable=True, server_default=sa.text('false')),
        sa.Column('verification_status', sa.String(length=50), nullable=True, server_default='unverified'),
        sa.Column('verification_message', sa.String(length=255), nullable=True),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. questions table
    op.create_table(
        'questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('difficulty', sa.String(length=20), nullable=True, server_default='medium'),
        sa.Column('target_role', sa.String(length=100), nullable=True, server_default='Software Engineer'),
        sa.Column('expected_keywords', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_questions_category', 'questions', ['category'])

    # 4. interviews table
    op.create_table(
        'interviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('target_role', sa.String(length=100), nullable=True, server_default='Software Engineer'),
        sa.Column('status', sa.String(length=30), nullable=True, server_default='in_progress'),
        sa.Column('overall_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('communication_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('technical_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('confidence_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('eye_contact_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('recording_path', sa.String(length=500), nullable=True),
        sa.Column('recording_url', sa.String(length=500), nullable=True),
        sa.Column('interview_photo', sa.String(length=255), nullable=True),
        sa.Column('warning_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('detected_faces_count', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('last_face_detection_time', sa.DateTime(), nullable=True),
        sa.Column('termination_reason', sa.String(length=255), nullable=True),
        sa.Column('proctoring_status', sa.String(length=50), nullable=True, server_default='clean'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. interview_responses table
    op.create_table(
        'interview_responses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('interview_id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('video_path', sa.String(length=500), nullable=True),
        sa.Column('video_url', sa.String(length=500), nullable=True),
        sa.Column('audio_path', sa.String(length=500), nullable=True),
        sa.Column('transcript', sa.Text(), nullable=True),
        sa.Column('relevance_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('technical_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('sentiment', sa.String(length=50), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('eye_contact_pct', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('head_stability_pct', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. reports table
    op.create_table(
        'reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('interview_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('communication_score', sa.Float(), nullable=False),
        sa.Column('technical_score', sa.Float(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('eye_contact_score', sa.Float(), nullable=False),
        sa.Column('target_role', sa.String(length=100), nullable=True, server_default='Software Engineer'),
        sa.Column('strengths', sa.Text(), nullable=True),
        sa.Column('improvements', sa.Text(), nullable=True),
        sa.Column('detailed_feedback', sa.Text(), nullable=True),
        sa.Column('recording_path', sa.String(length=500), nullable=True),
        sa.Column('recording_url', sa.String(length=500), nullable=True),
        sa.Column('generated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('interview_id')
    )

    # 7. interview_proctoring_violations table
    op.create_table(
        'interview_proctoring_violations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('interview_id', sa.Integer(), nullable=False),
        sa.Column('faces_detected', sa.Integer(), nullable=False),
        sa.Column('violation_type', sa.String(length=50), nullable=False),
        sa.Column('message', sa.String(length=255), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 8. email_otps table
    op.create_table(
        'email_otps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('otp_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('last_sent_at', sa.DateTime(), nullable=True),
        sa.Column('attempts', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('is_used', sa.Boolean(), nullable=True, server_default=sa.text('false')),
        sa.Column('purpose', sa.String(length=50), nullable=True, server_default='candidate_registration'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_email_otps_email', 'email_otps', ['email'])

    # 9. candidate_files table (Supabase Storage object references)
    op.create_table(
        'candidate_files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('candidate_id', sa.String(length=50), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('interview_id', sa.Integer(), nullable=True),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('object_key', sa.String(length=500), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('file_size', sa.BigInteger(), nullable=True, server_default='0'),
        sa.Column('storage_provider', sa.String(length=20), nullable=True, server_default='supabase'),
        sa.Column('local_path', sa.String(length=500), nullable=True),
        sa.Column('public_url', sa.String(length=500), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_candidate_files_cid', 'candidate_files', ['candidate_id'])
    op.create_index('ix_candidate_files_ft', 'candidate_files', ['file_type'])
    op.create_index('ix_candidate_files_key', 'candidate_files', ['object_key'])


def downgrade() -> None:
    op.drop_table('candidate_files')
    op.drop_table('email_otps')
    op.drop_table('interview_proctoring_violations')
    op.drop_table('reports')
    op.drop_table('interview_responses')
    op.drop_table('interviews')
    op.drop_table('questions')
    op.drop_table('resumes')
    op.drop_table('users')
