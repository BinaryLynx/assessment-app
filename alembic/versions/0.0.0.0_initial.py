"""0.0.0.0_initial

Revision ID: 0.0.0.0
Revises: 
Create Date: 2024-02-13 09:12:42.833478

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0.0.0.0"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;')
    op.execute("CREATE SCHEMA IF NOT EXISTS tables")
    op.execute("CREATE SCHEMA IF NOT EXISTS refs")

    op.create_table(
        "scale",
        sa.Column("id", sa.Text(), server_default=sa.text("public.uuid_generate_v4()"), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("max_value", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="refs",
    )

    op.create_table(
        "direction",
        sa.Column("id", sa.Text(), server_default=sa.text("public.uuid_generate_v4()"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        schema="refs",
    )
    op.create_table(
        "inspection_organ_type",
        sa.Column("id", sa.Text(), server_default=sa.text("public.uuid_generate_v4()"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="refs",
    )
    op.create_table(
        "inspection_target",
        sa.Column("id", sa.Text(), server_default=sa.text("public.uuid_generate_v4()"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        schema="tables",
    )
    op.create_table(
        "user_info",
        sa.Column("id", sa.Text(), server_default=sa.text("public.uuid_generate_v4()"), nullable=False),
        sa.Column("role_name", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="tables",
    )
    op.create_table(
        "topic",
        sa.Column("id", sa.Text(), server_default=sa.text("public.uuid_generate_v4()"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("direction_id", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["direction_id"], ["refs.direction.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        schema="refs",
    )
    op.create_table(
        "inspection_organ",
        sa.Column("id", sa.Text(), server_default=sa.text("public.uuid_generate_v4()"), nullable=False),
        sa.Column("parent_id", sa.Text(), nullable=True),
        sa.Column("path", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("short_name", sa.Text(), nullable=False),
        sa.Column("type_id", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["parent_id"], ["tables.inspection_organ.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["type_id"], ["refs.inspection_organ_type.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        schema="tables",
    )
    op.create_table(
        "grade",
        # sa.Column("id", sa.Text(), server_default=sa.text("public.uuid_generate_v4()"), nullable=False),
        sa.Column("value", sa.Float(), nullable=False, server_default=sa.text("1")),
        sa.Column("scale_id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["scale_id"], ["refs.scale.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("scale_id", "value"),
        schema="refs",
    )
    op.create_table(
        "inspection_result",
        sa.Column("id", sa.Text(), server_default=sa.text("public.uuid_generate_v4()"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("inspection_organ_id", sa.Text(), nullable=True),
        sa.Column("inspection_target_id", sa.Text(), nullable=True),
        sa.Column("operator_id", sa.Text(), nullable=False),
        sa.Column("grade", sa.Float(), nullable=True),
        sa.Column("created_date", sa.DateTime(), nullable=False),
        sa.Column("updated_date", sa.DateTime(), nullable=False),
        sa.Column("inspection_date", sa.DateTime(), nullable=True),
        sa.Column("files", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["inspection_organ_id"], ["tables.inspection_organ.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["inspection_target_id"], ["tables.inspection_target.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["operator_id"], ["tables.user_info.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        schema="tables",
    )
    op.create_table(
        "direction_result",
        sa.Column("id", sa.Text(), server_default=sa.text("public.uuid_generate_v4()"), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("direction_id", sa.Text(), nullable=True),
        sa.Column("inspection_result_id", sa.Text(), nullable=True),
        sa.Column("grade", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["direction_id"], ["refs.direction.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["inspection_result_id"], ["tables.inspection_result.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        schema="tables",
    )
    op.create_table(
        "topic_result",
        sa.Column("id", sa.Text(), server_default=sa.text("public.uuid_generate_v4()"), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("topic_id", sa.Text(), nullable=True),
        sa.Column("direction_result_id", sa.Text(), nullable=True),
        sa.Column("grade", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["direction_result_id"], ["tables.direction_result.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["topic_id"], ["refs.topic.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        schema="tables",
    )

    op.create_table(
        "inspection_target_type",
        sa.Column("id", sa.Text(), server_default=sa.text("public.uuid_generate_v4()"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("scale_id", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["scale_id"], ["refs.scale.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        schema="refs",
    )
    op.create_table(
        "inspection_target_type_direction_rel",
        sa.Column("inspection_target_type_id", sa.Text(), nullable=False),
        sa.Column("direction_id", sa.Text(), nullable=False),
        sa.Column("is_critical", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("weight", sa.Float(), nullable=False, server_default=sa.text("1.0")),
        sa.Column("is_ignored", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("scale_id", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["scale_id"], ["refs.scale.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["direction_id"], ["refs.direction.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["inspection_target_type_id"], ["refs.inspection_target_type.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("inspection_target_type_id", "direction_id"),
        schema="refs",
    )
    op.create_table(
        "inspection_target_type_topic_rel",
        sa.Column("inspection_target_type_id", sa.Text(), nullable=False),
        sa.Column("topic_id", sa.Text(), nullable=False),
        sa.Column("is_critical", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("weight", sa.Float(), nullable=False, server_default=sa.text("1.0")),
        sa.Column("is_ignored", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("scale_id", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["scale_id"], ["refs.scale.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["inspection_target_type_id"], ["refs.inspection_target_type.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["topic_id"], ["refs.topic.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("inspection_target_type_id", "topic_id"),
        schema="refs",
    )
    op.add_column("inspection_target", sa.Column("type_id", sa.Text(), nullable=True), schema="tables")
    op.create_foreign_key(
        None,
        "inspection_target",
        "inspection_target_type",
        ["type_id"],
        ["id"],
        source_schema="tables",
        referent_schema="refs",
    )

    op.create_table(
        "grade_criteria_direction",
        sa.Column("inspection_target_type_id", sa.Text(), nullable=False),
        sa.Column("direction_id", sa.Text(), nullable=False),
        sa.Column("direction_grade", sa.Float(), nullable=False),
        sa.Column("result_grade", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["inspection_target_type_id", "direction_id"],
            [
                "refs.inspection_target_type_direction_rel.inspection_target_type_id",
                "refs.inspection_target_type_direction_rel.direction_id",
            ],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("inspection_target_type_id", "direction_id", "direction_grade"),
        schema="refs",
    )
    op.create_table(
        "grade_criteria_topic",
        sa.Column("inspection_target_type_id", sa.Text(), nullable=False),
        sa.Column("topic_id", sa.Text(), nullable=False),
        sa.Column("topic_grade", sa.Float(), nullable=False),
        sa.Column("result_grade", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["inspection_target_type_id", "topic_id"],
            [
                "refs.inspection_target_type_topic_rel.inspection_target_type_id",
                "refs.inspection_target_type_topic_rel.topic_id",
            ],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("inspection_target_type_id", "topic_id", "topic_grade"),
        schema="refs",
    )

    # ### end Alembic commands ###

    # РАЗДЕЛ СОЗДАНИЕ РОЛЕЙ
    # логические роли
    op.execute(
        """
        CREATE ROLE is_operator;
        CREATE ROLE is_role;
        CREATE ROLE is_subject;
        CREATE ROLE is_admin;
        CREATE ROLE is_super_admin;
        """
    )

    # создание ролей соответствующие требуемым бизнес-ролям (наследуют пермишены)
    op.execute(
        """
        CREATE ROLE role_super_operator;
        CREATE ROLE role_operator;
        CREATE ROLE role_inspector;
        """
    )
    op.execute(
        """
        GRANT is_role TO role_super_operator;
        GRANT is_role TO role_operator;
        GRANT is_role TO role_inspector;
        """
    )
    # Создание ролей для RLS (описательные роли)
    op.execute(
        """
        CREATE ROLE rls_crud_own_io;
        CREATE ROLE rls_select_children_io;
        CREATE ROLE rls_select_own_io;
        """
    )
    op.execute(
        """
        COMMENT ON ROLE role_operator IS 'Оператор';
        COMMENT ON ROLE role_super_operator IS 'Супер оператор';
        COMMENT ON ROLE role_inspector IS 'Инспектор';
        """
    )
    # создание пользователей (наследуют роли, субъекты, принадлежность информации)
    op.execute(
        """
        CREATE USER petrovpp PASSWORD '1234';
        CREATE USER antonovaa PASSWORD '1234';
        """
    )
    # CREATE USER sidorovss WITH SUPERUSER PASSWORD '21380';
    op.execute(
        """
        INSERT INTO tables.user_info (id, role_name, name) VALUES 
        ('1', 'petrovpp', 'Петров'),
        ('2', 'antonovaa', 'Антонов')
        
        """
    )
    # ('3', 'sidorovss', 'Сидоров')

    op.execute(
        """
        GRANT is_operator TO antonovaa;
        GRANT is_operator TO petrovpp;
        
        GRANT role_inspector TO petrovpp;
        GRANT role_super_operator TO antonovaa;
        """
    )
    # GRANT is_admin TO petrovpp;
    # GRANT is_super_admin TO sidorovss;

    op.execute(
        """
        COMMENT ON role petrovpp IS 'Петров Петр Петрович';
        COMMENT ON role antonovaa IS 'Антонов Антон Антонович';
        """
    )
    # COMMENT ON role sidorovss IS 'Сидоров Сидор Сидорович';

    # создание схем
    op.execute(
        """
        GRANT USAGE ON SCHEMA tables TO is_operator;
        GRANT USAGE ON SCHEMA tables TO is_admin;
        GRANT USAGE ON SCHEMA tables TO is_super_admin;
        """
    )

    # создание ролей грантов
    op.execute(
        """
        CREATE ROLE perm_inspection_result_select;
        CREATE ROLE perm_inspection_result_crud;
        
        """
    )

    # определение правил грантов для таблиц
    op.execute(
        """
        GRANT SELECT,INSERT,UPDATE,DELETE ON tables.inspection_result TO perm_inspection_result_crud;
        GRANT SELECT ON tables.inspection_result TO perm_inspection_result_select;
        
        GRANT SELECT,INSERT,UPDATE,DELETE ON tables.inspection_organ TO perm_inspection_result_crud;
        GRANT SELECT ON tables.inspection_organ TO perm_inspection_result_select;
        
        GRANT SELECT,INSERT,UPDATE,DELETE ON tables.direction_result TO perm_inspection_result_crud;
        GRANT SELECT ON tables.direction_result TO perm_inspection_result_select;
        
        GRANT SELECT,INSERT,UPDATE,DELETE ON tables.topic_result TO perm_inspection_result_crud;
        GRANT SELECT ON tables.topic_result TO perm_inspection_result_select;
        """
    )

    # Включение RLS для таблицы
    op.execute("ALTER TABLE tables.inspection_result ENABLE ROW LEVEL SECURITY;")

    # Создание рлс
    op.execute(
        """
        CREATE POLICY rls_crud_own_io
        ON tables.inspection_result
        AS PERMISSIVE
        FOR ALL
        TO rls_crud_own_io
        USING ((inspection_organ_id IN ( WITH curr_user_subj_id AS (
             SELECT inspection_organ.id
               FROM tables.inspection_organ
              WHERE (inspection_organ.path = ( SELECT pg_roles.rolname
                       FROM (pg_auth_members mem
                         JOIN pg_roles ON ((pg_roles.oid = mem.member)))
                      WHERE ((mem.member IN ( SELECT pg_auth_members.roleid
                               FROM pg_auth_members
                              WHERE (pg_auth_members.member = ( SELECT pg_roles_1.oid
                                       FROM pg_roles pg_roles_1
                                      WHERE (pg_roles_1.rolname = CURRENT_USER))))) AND (mem.roleid = ( SELECT pg_roles_1.oid
                               FROM pg_roles pg_roles_1
                              WHERE (pg_roles_1.rolname = 'is_subject'::name))))))
            )
        SELECT curr_user_subj_id.id
        FROM curr_user_subj_id)));
        """
    )

    op.execute(
        """
        CREATE POLICY rls_select_children_io
        ON tables.inspection_result
        AS PERMISSIVE
        FOR ALL
        TO rls_select_children_io
        USING ((inspection_organ_id IN ( WITH RECURSIVE subj AS (
             SELECT inspection_organ.id,
                inspection_organ.parent_id
               FROM tables.inspection_organ
              WHERE (inspection_organ.path = ( SELECT pg_roles.rolname
                       FROM (pg_auth_members mem
                         JOIN pg_roles ON ((pg_roles.oid = mem.member)))
                      WHERE ((mem.member IN ( SELECT pg_auth_members.roleid
                               FROM pg_auth_members
                              WHERE (pg_auth_members.member = ( SELECT pg_roles_1.oid
                                       FROM pg_roles pg_roles_1
                                      WHERE (pg_roles_1.rolname = CURRENT_USER))))) AND (mem.roleid = ( SELECT pg_roles_1.oid
                               FROM pg_roles pg_roles_1
                              WHERE (pg_roles_1.rolname = 'is_subject'::name))))))
            UNION
             SELECT inspection_organ.id,
                inspection_organ.parent_id
               FROM (tables.inspection_organ
                 JOIN subj subj_1 ON ((inspection_organ.parent_id = subj_1.id)))
            )
        SELECT subj.id
        FROM subj)));
        """
    )

    op.execute(
        """
        CREATE POLICY rls_select_own_io
        ON tables.inspection_result
        AS PERMISSIVE
        FOR ALL
        TO rls_select_own_io
        USING ((inspection_organ_id IN ( WITH curr_user_subj_id AS (
             SELECT inspection_organ.id
               FROM tables.inspection_organ
              WHERE (inspection_organ.path = ( SELECT pg_roles.rolname
                       FROM (pg_auth_members mem
                         JOIN pg_roles ON ((pg_roles.oid = mem.member)))
                      WHERE ((mem.member IN ( SELECT pg_auth_members.roleid
                               FROM pg_auth_members
                              WHERE (pg_auth_members.member = ( SELECT pg_roles_1.oid
                                       FROM pg_roles pg_roles_1
                                      WHERE (pg_roles_1.rolname = CURRENT_USER))))) AND (mem.roleid = ( SELECT pg_roles_1.oid
                               FROM pg_roles pg_roles_1
                              WHERE (pg_roles_1.rolname = 'is_subject'::name))))))
            )
        SELECT curr_user_subj_id.id
        FROM curr_user_subj_id)));
        """
    )

    # бизнес-роли
    op.execute(
        """
        GRANT rls_crud_own_io to role_super_operator;
        GRANT rls_select_children_io to role_super_operator;
        GRANT rls_crud_own_io to role_operator;
        GRANT rls_select_own_io to role_inspector;

        GRANT perm_inspection_result_select to role_inspector;
        GRANT perm_inspection_result_crud to role_super_operator,role_operator;
        """
    )

    # роли проверяющих органов
    op.execute(
        """
        CREATE ROLE "1";
        GRANT is_subject to "1";
        CREATE ROLE "1.2";
        GRANT is_subject to "1.2";
        
        GRANT "1" to "1.2";
        GRANT "1" to petrovpp;
        GRANT "1" to antonovaa;
        
        COMMENT ON role "1" IS 'ООО Паровоз';
        COMMENT ON role "1.2" IS 'ООО Вагон';
        """
    )


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    op.execute(
        """
        DROP SCHEMA IF EXISTS tables CASCADE;
        DROP SCHEMA IF EXISTS refs CASCADE;

        DROP ROLE IF EXISTS is_operator;
        DROP ROLE IF EXISTS is_role;
        DROP ROLE IF EXISTS is_subject;
        DROP ROLE IF EXISTS is_admin;
        DROP ROLE IF EXISTS is_super_admin;

        DROP ROLE IF EXISTS role_super_operator;
        DROP ROLE IF EXISTS role_operator;
        DROP ROLE IF EXISTS role_inspector;

        DROP ROLE IF EXISTS rls_crud_own_io;
        DROP ROLE IF EXISTS rls_select_children_io;
        DROP ROLE IF EXISTS rls_select_own_io;

        DROP ROLE IF EXISTS petrovpp;
        DROP ROLE IF EXISTS antonovaa;
        DROP ROLE IF EXISTS sidorovss;

        DROP ROLE IF EXISTS perm_inspection_result_select;
        DROP ROLE IF EXISTS perm_inspection_result_crud;
        """
    )
    op.execute(
        """
        DROP ROLE IF EXISTS "1";
        DROP ROLE IF EXISTS "1.2";
        """
    )