"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "source_videos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "source_type",
            sa.Enum("youtube_url", "upload", name="source_type"),
            nullable=False,
        ),
        sa.Column("source_url", sa.String(2048), nullable=True),
        sa.Column("original_filename", sa.String(512), nullable=True),
        sa.Column("title", sa.String(512), nullable=True),
        sa.Column("storage_path", sa.String(1024), nullable=True),
        sa.Column("duration_seconds", sa.Float, nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "pending", "downloading", "downloaded", "failed",
                name="source_video_status",
            ),
            nullable=False,
        ),
        sa.Column("error_message", sa.String(2048), nullable=True),
    )
    op.create_index("ix_source_videos_user_id", "source_videos", ["user_id"])

    op.create_table(
        "transcripts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "source_video_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("source_videos.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("provider", sa.String(64), nullable=False),
        sa.Column("language", sa.String(16), nullable=True),
        sa.Column("segments", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("full_text", sa.Text, nullable=False, server_default=""),
    )
    op.create_index("ix_transcripts_source_video_id", "transcripts", ["source_video_id"])

    op.create_table(
        "recommended_cuts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "source_video_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("source_videos.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("start_seconds", sa.Float, nullable=False),
        sa.Column("end_seconds", sa.Float, nullable=False),
        sa.Column(
            "reason",
            sa.Enum(
                "silence", "filler_word", "false_start", "dead_air", "redundant",
                name="cut_reason",
            ),
            nullable=False,
        ),
        sa.Column("confidence", sa.Float, nullable=True),
        sa.Column(
            "detected_by",
            sa.Enum("ffmpeg_silence", "claude", name="cut_detected_by"),
            nullable=False,
        ),
        sa.Column("reasoning", sa.Text, nullable=True),
        sa.Column(
            "user_decision",
            sa.Enum("pending", "accepted", "rejected", name="cut_decision"),
            nullable=False,
        ),
    )
    op.create_index("ix_recommended_cuts_source_video_id", "recommended_cuts", ["source_video_id"])

    op.create_table(
        "chapters",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "source_video_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("source_videos.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("start_seconds", sa.Float, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("order_index", sa.Integer, nullable=False),
    )
    op.create_index("ix_chapters_source_video_id", "chapters", ["source_video_id"])

    op.create_table(
        "music_segments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "source_video_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("source_videos.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("start_seconds", sa.Float, nullable=False),
        sa.Column("end_seconds", sa.Float, nullable=False),
        sa.Column("confidence", sa.Float, nullable=False),
        sa.Column(
            "action", sa.Enum("mute", "duck", name="music_action"), nullable=False
        ),
    )
    op.create_index("ix_music_segments_source_video_id", "music_segments", ["source_video_id"])

    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "source_video_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("source_videos.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "job_type",
            sa.Enum(
                "ingest", "transcribe", "detect_silence", "detect_music", "analyze",
                "render_longform", "select_tiktok", "render_tiktok",
                "select_micro", "render_micro",
                name="job_type",
            ),
            nullable=False,
        ),
        sa.Column("celery_task_id", sa.String(255), nullable=True),
        sa.Column(
            "status",
            sa.Enum("queued", "running", "succeeded", "failed", name="job_status"),
            nullable=False,
        ),
        sa.Column("progress_pct", sa.Integer, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_jobs_source_video_id", "jobs", ["source_video_id"])

    op.create_table(
        "long_form_exports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "source_video_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("source_videos.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("storage_path", sa.String(1024), nullable=True),
        sa.Column("captions_srt_path", sa.String(1024), nullable=True),
        sa.Column("captions_vtt_path", sa.String(1024), nullable=True),
        sa.Column("captions_burned_in", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("applied_cut_ids", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("title_used", sa.String(512), nullable=True),
        sa.Column("chapters_used", postgresql.JSONB, nullable=False, server_default="[]"),
    )
    op.create_index("ix_long_form_exports_source_video_id", "long_form_exports", ["source_video_id"])

    op.create_table(
        "short_clips",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "long_form_export_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("long_form_exports.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("start_seconds", sa.Float, nullable=False),
        sa.Column("end_seconds", sa.Float, nullable=False),
        sa.Column("storage_path", sa.String(1024), nullable=True),
        sa.Column("selection_reasoning", sa.Text, nullable=True),
        sa.Column("hook_score", sa.Float, nullable=True),
        sa.Column(
            "crop_strategy",
            sa.Enum("static_center", "face_tracked", name="crop_strategy"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("selected", "rendering", "rendered", "failed", name="clip_status"),
            nullable=False,
        ),
    )
    op.create_index("ix_short_clips_long_form_export_id", "short_clips", ["long_form_export_id"])

    op.create_table(
        "micro_clips",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "short_clip_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("short_clips.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("start_seconds", sa.Float, nullable=False),
        sa.Column("end_seconds", sa.Float, nullable=False),
        sa.Column("storage_path", sa.String(1024), nullable=True),
        sa.Column("selection_reasoning", sa.Text, nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "selected", "rendering", "rendered", "failed", name="micro_clip_status"
            ),
            nullable=False,
        ),
    )
    op.create_index("ix_micro_clips_short_clip_id", "micro_clips", ["short_clip_id"])


def downgrade() -> None:
    op.drop_table("micro_clips")
    op.drop_table("short_clips")
    op.drop_table("long_form_exports")
    op.drop_table("jobs")
    op.drop_table("music_segments")
    op.drop_table("chapters")
    op.drop_table("recommended_cuts")
    op.drop_table("transcripts")
    op.drop_table("source_videos")
    op.drop_table("users")

    sa.Enum(name="micro_clip_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="clip_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="crop_strategy").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="job_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="job_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="music_action").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="cut_decision").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="cut_detected_by").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="cut_reason").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="source_video_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="source_type").drop(op.get_bind(), checkfirst=True)
