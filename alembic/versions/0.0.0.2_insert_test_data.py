"""0.0.0.2_insert_test_data

Revision ID: 148a758bcfd9
Revises: 0.0.0.2
Create Date: 2024-02-13 09:12:42.833478

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0.0.0.2"
down_revision: str = "0.0.0.0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    op.execute(
        """
        INSERT INTO refs.scale(id) VALUES
        ('1'),
        ('2'),
        ('3')
        """
    )

    op.execute(
        """
        INSERT INTO refs.direction(id, name) VALUES
        ('1', 'Внешний вид товара'),
        ('2', 'Качество товара'),
        ('3', 'Экологичность товара')
        """
    )

    op.execute(
        """
        INSERT INTO refs.topic(id, name, direction_id) VALUES
        ('1', 'признаки перезрелости', '1'),
        ('2', 'видимые механические повреждения', '1'),
        ('3', 'Наличие неприятного запаха', '1'),
                
        ('4', 'Качество материалов', '2'),
        ('5', 'Качество сырья', '2'),
        ('6', 'Рейтинг производителя', '2'),
        ('7', 'Соответствие стандартам качества', '2'),
        
        ('8', 'Использование ГМО', '3'),
        ('9', 'Экологичность материалов', '3')
        """
    )

    op.execute(
        """
        INSERT INTO refs.inspection_organ_type(id, name) VALUES 
        (1, 'Бюро оценки')
        """
    )

    op.execute(
        """
        insert into tables.inspection_organ(id, parent_id, path, name, short_name, type_id) values
        ('1',null,'1','ООО Паровоз','Паровоз','1'),
        ('2','1','1.2','ООО Голубой вагон','Голубой вагон','1')
        """
    )

    op.execute(
        """
        INSERT INTO refs.inspection_target_type(id, name, scale_id) VALUES
        ('1', 'Товар питания','2'),
        ('2', 'Товар электроники','2'),
        ('3', 'Товар бытовой','2')
        """
    )

    op.execute(
        """
        INSERT INTO tables.inspection_target (id, name,type_id) VALUES
        ('1', 'Яблоко', '1'),
        ('2', 'Банан', '1'),
        ('3', 'Фен', '2'),
        ('4', 'Бумажные полотенца', '3')
        """
    )

    op.execute(
        """
        INSERT INTO refs.grade (name, value , scale_id) VALUES
        ('Приемлемо',3,'3'),
        ('Ограничено приемлемо',2,'3'),
        ('Не приемлемо',1,'3'),
        ('Зачтено',2,'2'),
        ('Не зачтено',1,'2'),
        ('Отлично',4,'1'),
        ('Хорошо',3,'1'),
        ('Удовлетворительно',2,'1'),
        ('Не удовлетворительно',1,'1')
        """
    )

    op.execute(
        """
        INSERT INTO tables.inspection_result (id, name, description, inspection_organ_id, inspection_target_id, operator_id, created_date, updated_date, grade) VALUES
        ('1','Инспекционная проверка 1','Инспекционная проверка 1','2','1','1','2024-01-23 14:28:27.908589','2024-01-23 14:28:27.908589', 2)
        """
    )

    op.execute(
        """
        INSERT INTO tables.direction_result (id, direction_id, inspection_result_id) VALUES
        ('1','1','1'),
        ('2','2','1')
        """
    )

    op.execute(
        """
        INSERT INTO tables.topic_result(id, topic_id, direction_result_id,grade) VALUES
        ('1','1','1',3),
        ('2','3','1',2),
        ('3','6','2',4),
        ('4','7','2',2)
        """
    )

    op.execute(
        """
        INSERT INTO refs.inspection_target_type_topic_rel(inspection_target_type_id, topic_id, scale_id)	VALUES
        ('1', '1','3'),
        ('1', '3','2'),
        ('1', '6','1'),
        ('1', '7','1'),
        ('1', '8','2'),

        ('2', '2','1'),
        ('2', '4','2'),
        ('2', '6','1'),
        ('2', '7','1'),
        ('2', '9','2'),

        ('3', '2','1'),
        ('3', '4','2'),
        ('3', '6','1'),
        ('3', '7','1')
        """
    )

    op.execute(
        """
        INSERT INTO refs.inspection_target_type_direction_rel(inspection_target_type_id, direction_id, scale_id)	VALUES
        ('1', '1','2'),
        ('1', '2','2'),
        ('1', '3','2'),
        ('2', '1','2'),
        ('2', '2','2'),
        ('2', '3','2')
        """
    )

    op.execute(
        """
        INSERT INTO refs.grade_criteria_topic(inspection_target_type_id,topic_id,result_grade,topic_grade)	VALUES
        ('1', '1', 2, 3),
        ('1', '1', 2, 2),
        ('1', '1', 1, 1),

        ('1', '3', 2, 2),
        ('1', '3', 1, 1),

        ('1', '6', 2, 4),
        ('1', '6', 2, 3),
        ('1', '6', 1, 2),
        ('1', '6', 1, 1),

        ('1', '7', 2, 4),
        ('1', '7', 1, 3),
        ('1', '7', 1, 2),
        ('1', '7', 1, 1),

        ('1', '8', 2, 2),
        ('1', '8', 1, 1),

        ('2', '2', 2, 4),
        ('2', '2', 2, 3),
        ('2', '2', 1, 2),
        ('2', '2', 1, 1),

        ('2', '4', 2, 2),
        ('2', '4', 1, 1),

        ('2', '6', 2, 4),
        ('2', '6', 1, 3),
        ('2', '6', 1, 2),
        ('2', '6', 1, 1),

        ('2', '7', 2, 4),
        ('2', '7', 2, 3),
        ('2', '7', 2, 2),
        ('2', '7', 1, 1),

        ('2', '9', 2, 2),
        ('2', '9', 1, 1)
        """
    )

    op.execute(
        """
        INSERT INTO refs.grade_criteria_direction(inspection_target_type_id,direction_id,result_grade,direction_grade)	VALUES
        ('1', '1', 2, 2),
        ('1', '1', 1, 1),
        ('1', '2', 2, 2),
        ('1', '2', 1, 1),
        ('1', '3', 2, 2),
        ('1', '3', 1, 1),
        ('2', '1', 2, 2),
        ('2', '1', 1, 1),
        ('2', '2', 2, 2),
        ('2', '2', 1, 1),
        ('2', '3', 2, 2),
        ('2', '3', 1, 1)
        """
    )

    pass


def downgrade():
    pass
