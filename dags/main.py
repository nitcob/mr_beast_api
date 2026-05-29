from airflow import DAG
from airflow.operators.python import PythonOperator

import pendulum
from datetime import datetime, timedelta
from api.video_stats import extract_video_data, get_playlist_id, get_video_ids, save_to_json

# timezone-aware start date using pendulum
local_tz = pendulum.timezone("America/New_York")

#Default Args
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1, tzinfo=local_tz),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    #'retries': 1,
    'max_active_runs': 1,
    'dagrun_timeout': timedelta(minutes=60),
    
    # 'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}

with DAG(
    dag_id="produce_json_file_with_video_stats",
    description="A DAG to extract video stats from YouTube and save them to a JSON file",
    default_args=default_args,
    schedule="0 14 * * *",  # Daily at 2 PM
    catchup=False,
    
    
) as dag:
    # Define tasks here
    get_playlist_id_task = PythonOperator(
        task_id='get_playlist_id',
        python_callable=get_playlist_id
    )
    
    video_ids_task = PythonOperator(
        task_id='get_video_ids',
        python_callable=get_video_ids,
        op_args=[get_playlist_id_task.output]
    )
    
    extract_data_task = PythonOperator(
        task_id='extract_video_data',
        python_callable=extract_video_data,
        op_args=[video_ids_task.output]
    )
    
    save_json_task = PythonOperator(
        task_id='save_to_json',
        python_callable=save_to_json,
        op_args=[extract_data_task.output]
    )

    # Set task dependencies
    get_playlist_id_task >> video_ids_task >> extract_data_task >> save_json_task
    