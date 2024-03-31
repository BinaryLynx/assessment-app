from datetime import datetime

from typing import List, Set


from sqlalchemy import Boolean, Float, ForeignKey, ForeignKeyConstraint, Text, func, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.base_models import Base


class UserInfo(Base):
    """Модель информации о пользователях."""

    __tablename__ = "user_info"
    __table_args__ = {"schema": "tables"}

    id: Mapped[str] = mapped_column(
        Text, primary_key=True, nullable=False, server_default=func.public.uuid_generate_v4()
    )
    role_name: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    inspections: Mapped[Set["InspectionResult"]] = relationship(
        "InspectionResult", back_populates="operator", uselist=True
    )


class Direction(Base):
    """Модель направления проверки."""

    __tablename__ = "direction"
    __table_args__ = {"schema": "refs"}

    id: Mapped[str] = mapped_column(
        Text, primary_key=True, nullable=False, server_default=func.public.uuid_generate_v4()
    )
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    topics: Mapped[Set["Topic"]] = relationship("Topic", back_populates="direction", uselist=True)
    # inspection_target_types: Mapped[Set["InspectionTargetType"]] = relationship(
    #     "InspectionTargetTypeDirectionRel", back_populates="direction"
    # )


class Topic(Base):
    """Модель поднаправления проверки."""

    __tablename__ = "topic"
    __table_args__ = {"schema": "refs"}

    id: Mapped[str] = mapped_column(
        Text, primary_key=True, nullable=False, server_default=func.public.uuid_generate_v4()
    )
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    direction_id: Mapped[str] = mapped_column(Text, ForeignKey("refs.direction.id", ondelete="CASCADE"), nullable=False)
    direction: Mapped["Direction"] = relationship(back_populates="topics", uselist=False)
    # inspection_target_types: Mapped[Set["InspectionTargetType"]] = relationship(
    #     "InspectionTargetTypeTopicRel", back_populates="topic"
    # )

    def __repr__(self) -> str:
        return f"<id: {self.id}, name: {self.name}, weight: {self.weight}, direction_id: {self.direction_id}>"


class Scale(Base):
    __tablename__ = "scale"
    __table_args__ = {"schema": "refs"}

    id: Mapped[str] = mapped_column(
        Text, primary_key=True, nullable=False, server_default=func.public.uuid_generate_v4()
    )
    name: Mapped[str] = mapped_column(Text, nullable=True)
    max_value: Mapped[float] = mapped_column(Float, nullable=True)
    topics: Mapped[List["InspectionTargetTypeTopicRel"]] = relationship(back_populates="scale")
    directions: Mapped[List["InspectionTargetTypeDirectionRel"]] = relationship(back_populates="scale")
    grades: Mapped[List["Grade"]] = relationship(back_populates="scale")


class Grade(Base):
    """Модель результатов оценок."""

    __tablename__ = "grade"
    __table_args__ = {"schema": "refs"}

    value: Mapped[float] = mapped_column(Float, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)

    scale_id: Mapped[str] = mapped_column(Text, ForeignKey("refs.scale.id"), primary_key=True)
    scale: Mapped["Scale"] = relationship(back_populates="grades")


class InspectionTarget(Base):
    """Модель проверяемого субъекта."""

    __tablename__ = "inspection_target"
    __table_args__ = {"schema": "tables"}

    id: Mapped[str] = mapped_column(
        Text, primary_key=True, nullable=False, server_default=func.public.uuid_generate_v4()
    )
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    type_id: Mapped[str] = mapped_column(Text, ForeignKey("refs.inspection_target_type.id"), nullable=True)
    inspections: Mapped[Set["InspectionResult"]] = relationship(
        "InspectionResult", back_populates="inspection_target", uselist=True
    )
    type: Mapped["InspectionTargetType"] = relationship()


class InspectionTargetType(Base):
    """Модель типа проверяющего органа."""

    __tablename__ = "inspection_target_type"
    __table_args__ = {"schema": "refs"}

    id: Mapped[str] = mapped_column(
        Text, primary_key=True, nullable=False, server_default=func.public.uuid_generate_v4()
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    directions: Mapped[Set["Direction"]] = relationship(
        "InspectionTargetTypeDirectionRel", back_populates="inspection_target_type"
    )
    topics: Mapped[Set["Topic"]] = relationship("InspectionTargetTypeTopicRel", back_populates="inspection_target_type")
    scale_id: Mapped[str] = mapped_column(Text, ForeignKey("refs.scale.id"), nullable=False)

    def __repr__(self) -> str:
        return f"<id: {self.id}, name: {self.name}>"


class InspectionResult(Base):
    """Модель результата проверки."""

    __tablename__ = "inspection_result"
    __table_args__ = {"schema": "tables"}

    id: Mapped[str] = mapped_column(
        Text, primary_key=True, nullable=False, server_default=func.public.uuid_generate_v4()
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    grade: Mapped[float] = mapped_column(Float, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    direction_results: Mapped[Set["DirectionResult"]] = relationship(
        back_populates="inspection_result", uselist=True, lazy="subquery"
    )
    inspection_organ_id: Mapped[str] = mapped_column(Text, ForeignKey("tables.inspection_organ.id"))
    inspection_organ: Mapped["InspectionOrgan"] = relationship(back_populates="inspections", uselist=False)
    inspection_target_id: Mapped[str] = mapped_column(
        Text, ForeignKey("tables.inspection_target.id", ondelete="SET NULL"), nullable=True
    )
    inspection_target: Mapped["InspectionTarget"] = relationship(back_populates="inspections", uselist=False)
    operator_id: Mapped[str] = mapped_column(Text, ForeignKey("tables.user_info.id"))
    operator: Mapped["UserInfo"] = relationship(back_populates="inspections", uselist=False)
    created_date: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False, default=datetime.now)
    updated_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=datetime.now, onupdate=datetime.now
    )
    inspection_date: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False, default=datetime.now)
    files: Mapped[List[str]] = mapped_column(JSON, nullable=True)

    def __repr__(self):
        return (
            f"<id: {self.id}, "
            f"name: {self.name}, "
            f"grade: {self.grade}, "
            f"description: {self.description}, "
            f"inspection_organ_id: {self.inspection_organ_id}, "
            f"inspection_target_id: {self.inspection_target_id}, "
            f"operator_id: {self.operator_id}>"
        )


class DirectionResult(Base):
    """Модель результата проверки по направлению."""

    __tablename__ = "direction_result"
    __table_args__ = {"schema": "tables"}

    id: Mapped[str] = mapped_column(
        Text, primary_key=True, nullable=False, server_default=func.public.uuid_generate_v4()
    )
    grade: Mapped[float] = mapped_column(Float, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    direction_id: Mapped[str] = mapped_column(Text, ForeignKey("refs.direction.id", ondelete="SET NULL"), nullable=True)
    direction: Mapped["Direction"] = relationship(uselist=False, lazy="joined")
    topic_results: Mapped[Set["TopicResult"]] = relationship(
        back_populates="direction_result", uselist=True, lazy="subquery"
    )
    inspection_result_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("tables.inspection_result.id", ondelete="CASCADE"),
        nullable=True,
    )
    inspection_result: Mapped["InspectionResult"] = relationship(back_populates="direction_results", uselist=False)

    def __repr__(self):
        return (
            f"<id: {self.id}, "
            f"grade: {self.grade}, "
            f"description: {self.description}, "
            f"direction_id: {self.direction_id}, "
            f"inspection_result_id: {self.inspection_result_id}>"
        )


class TopicResult(Base):
    """Модель результата проверки по поднаправлению."""

    __tablename__ = "topic_result"
    __table_args__ = {"schema": "tables"}

    id: Mapped[str] = mapped_column(
        Text, primary_key=True, nullable=False, server_default=func.public.uuid_generate_v4()
    )
    grade: Mapped[float] = mapped_column(Float, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    topic_id: Mapped[str] = mapped_column(Text, ForeignKey("refs.topic.id", ondelete="SET NULL"), nullable=True)
    topic: Mapped["Topic"] = relationship(uselist=False, lazy="selectin")
    direction_result_id: Mapped[str] = mapped_column(
        Text, ForeignKey("tables.direction_result.id", ondelete="CASCADE"), nullable=True
    )
    direction_result: Mapped["DirectionResult"] = relationship(back_populates="topic_results", uselist=False)

    def __repr__(self):
        return (
            f"<id: {self.id}, "
            f"grade: {self.grade}, "
            f"description: {self.description}, "
            f"topic_id: {self.topic_id}, "
            f"direction_result_id: {self.direction_result_id}>"
        )


class InspectionOrgan(Base):
    """Модель проверяющего органа."""

    __tablename__ = "inspection_organ"
    __table_args__ = {"schema": "tables"}

    id: Mapped[str] = mapped_column(
        Text, primary_key=True, nullable=False, server_default=func.public.uuid_generate_v4()
    )
    parent_id: Mapped[str] = mapped_column(Text, ForeignKey("tables.inspection_organ.id"), nullable=True)
    path: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    short_name: Mapped[str] = mapped_column(Text, nullable=False)
    type_id: Mapped[str] = mapped_column(Text, ForeignKey("refs.inspection_organ_type.id"), nullable=True)
    inspections: Mapped[Set["InspectionResult"]] = relationship(
        "InspectionResult", back_populates="inspection_organ", uselist=True
    )

    def __repr__(self) -> str:
        return f"<id: {self.id}, name: {self.name}, short_name: {self.short_name}, type_id: {self.type_id}>"


class InspectionOrganType(Base):
    """Модель типа проверяющего органа."""

    __tablename__ = "inspection_organ_type"
    __table_args__ = {"schema": "refs"}

    id: Mapped[str] = mapped_column(
        Text, primary_key=True, nullable=False, server_default=func.public.uuid_generate_v4()
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self) -> str:
        return f"<id: {self.id}, name: {self.name}>"


class InspectionTargetTypeDirectionRel(Base):
    """Модель связи типа проверяющего органа с направлением."""

    __tablename__ = "inspection_target_type_direction_rel"
    __table_args__ = {"schema": "refs"}

    inspection_target_type_id: Mapped[str] = mapped_column(
        Text, ForeignKey("refs.inspection_target_type.id"), primary_key=True
    )
    direction_id: Mapped[str] = mapped_column(Text, ForeignKey("refs.direction.id"), primary_key=True)
    is_critical: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=float(1))
    is_ignored: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    scale_id: Mapped[str] = mapped_column(Text, ForeignKey("refs.scale.id"), nullable=False)
    scale: Mapped["Scale"] = relationship(back_populates="directions")
    direction: Mapped["Direction"] = relationship("Direction")
    inspection_target_type: Mapped["InspectionTargetType"] = relationship(
        "InspectionTargetType", back_populates="directions"
    )


class InspectionTargetTypeTopicRel(Base):
    """Модель связи типа проверяющего органа с поднаправлением."""

    __tablename__ = "inspection_target_type_topic_rel"
    __table_args__ = {"schema": "refs"}

    inspection_target_type_id: Mapped[str] = mapped_column(
        Text, ForeignKey("refs.inspection_target_type.id"), primary_key=True
    )
    topic_id: Mapped[str] = mapped_column(Text, ForeignKey("refs.topic.id"), primary_key=True)

    is_critical: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=float(1))
    is_ignored: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    scale_id: Mapped[str] = mapped_column(Text, ForeignKey("refs.scale.id"), nullable=False)
    scale: Mapped["Scale"] = relationship(back_populates="topics")
    topic: Mapped["Topic"] = relationship("Topic")
    inspection_target_type: Mapped["InspectionTargetType"] = relationship(
        "InspectionTargetType", back_populates="topics"
    )

class GradeCriteriaDirection(Base):
    """Критерии оценки типа подразделения для направлений."""

    __tablename__ = "grade_criteria_direction"

    inspection_target_type_id: Mapped[str] = mapped_column(Text, primary_key=True)
    direction_id: Mapped[str] = mapped_column(Text, primary_key=True)
    direction_grade: Mapped[float] = mapped_column(Float, primary_key=True)
    result_grade: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            [inspection_target_type_id, direction_id],
            [InspectionTargetTypeDirectionRel.inspection_target_type_id, InspectionTargetTypeDirectionRel.direction_id],
        ),
        {"schema": "refs"},
    )


class GradeCriteriaTopic(Base):
    """Критерии оценки типа подразделения для поднаправлений."""

    __tablename__ = "grade_criteria_topic"

    inspection_target_type_id: Mapped[str] = mapped_column(Text, primary_key=True)
    topic_id: Mapped[str] = mapped_column(Text, primary_key=True)
    topic_grade: Mapped[float] = mapped_column(Float, primary_key=True)
    result_grade: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            [inspection_target_type_id, topic_id],
            [InspectionTargetTypeTopicRel.inspection_target_type_id, InspectionTargetTypeTopicRel.topic_id],
        ),
        {"schema": "refs"},
    )
