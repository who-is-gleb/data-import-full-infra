from airflow.models import DagBag


def test_dagbag():
    """
    Not very comprehensive tests but they can serve as a basis for future enhancements
    """
    dagbag = DagBag(include_examples=False)
    assert not dagbag.import_errors

    for dag_id, dag in dagbag.dags.items():
        assert dag.tags


if __name__ == '__main__':
    test_dagbag()