import subprocess
import json
import logging
import os
import socket

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Elasticsearch credentials and query details
elasticsearch_url = os.environt['ELASTIC_URL']
username = os.environment['ELASTIC_USER'] 
password = os.environment['ELASTIC_PASSWORD']

#Event ID
event_id_file_path= "/tmp/event_id.txt"

# Directory path containing query files
query_directory_path = "/opt/queries/fabricantes/checkpoint"

nc_host = "10.0.1.5"  # Change to your desired host
nc_port = 7070          # Change to your desired port

# Read and update last event ID
def manage_event_id(increment=True):
    if os.path.exists(event_id_file_path):
        with open(event_id_file_path, 'r+') as file:
            last_id = int(file.read().strip())
            if increment:
                last_id += 1
                file.seek(0)
                file.write(str(last_id))
            return last_id
    else:
        with open(event_id_file_path, 'w') as file:
            file.write('0')
        return 0

# List all JSON files in the directory
query_files = [f for f in os.listdir(query_directory_path) if f.endswith('.json')]
logging.info(f"Found {len(query_files)} JSON files in the directory: {query_directory_path}")

# Iterate over each JSON file and run the script
for query_file in query_files:
    query_file_path = os.path.join(query_directory_path, query_file)
    logging.info(f"Processing query file: {query_file_path}")

    # Read the query from the JSON file
    try:
        with open(query_file_path, 'r') as query_file_handle:
            query = json.load(query_file_handle)
    except FileNotFoundError:
        logging.error(f"Query file not found: {query_file_path}")
        continue
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from query file: {query_file_path}")
        continue

    # Convert query to JSON string
    query_json = json.dumps(query)

    # Define curl command
    curl_command = [
        "curl", "-X", "POST", "-k", elasticsearch_url,
        "-u", f"{username}:{password}",
        "-H", "Content-Type: application/json",
        "-d", query_json
    ]

    # Run curl command and capture output
    try:
        result = subprocess.run(curl_command, capture_output=True, text=True, check=True)
        output_json = result.stdout.strip()

        # Parse the JSON response
        response = json.loads(output_json)

        # Process aggregations to extract event_id and subscription_id
        aggregations = response.get('aggregations', {})
        event_count = aggregations.get('event_count', {})
        buckets = event_count.get('buckets', [])

        for bucket in buckets:
            l_event_id = bucket.get('key')  # Extract event_id from each bucket
            hits = bucket.get('show_fields', {}).get('hits', {}).get('hits', [])
            l_doc_count = bucket['doc_count']

            # Initialize the event ID for this bucket
            #if hits:
            for query_file in query_files:
                new_event_id = manage_event_id()  # Generate a new event ID for this bucket
                rule_name = os.path.splitext(query_file)[0]  # Remove the .json extension

            for hit in hits:
                source = hit.get('_source', {})
                l_subscription_id = source.get('azure', {}).get('subscription_id')
                l_checkpoint_user = source.get('checkpoint', {}).get('user')  # Extract checkpoint.user
                l_source_ip = source.get('source', {}).get('ip')  # Extract source.ip
                l_so_user = source.get('so', {}).get('user')  # Extract source.ip
                l_event_action = source.get('event', {}).get('action')  # Extract source.ip
                l_observer_product = source.get ('observer', {}).get('product')
                l_so_client_version = source.get('so', {}).get('client_version')
                l_source_geo_country_name= source.get('source', {}).get('geo',{}).get('country_name')
                l_host_os_name = source.get('host', {}).get('os',{}).get('name')
                l_environment = source.get('environment', {})
                l_tags = source.get('tags',{})
                # Log extracted values
                
                #if l_event_id is not None:
                #    logging.info(f"Event ID: {l_event_id}")

                if l_subscription_id is not None:
                    logging.info(f"Subscription ID: {l_subscription_id}")
                
                if l_doc_count is not None:
                    logging.info(f"Total Events: {l_doc_count}")
                
                if l_observer_product is not None:
                    logging.info(f"Observer product: {l_observer_product}")  
               
                if l_so_client_version is not None:
                    logging.info(f"Client Version: {l_so_client_version}")  
                
                if l_source_ip is not None:
                    logging.info(f"Source IP: {l_source_ip}")  
                
                if l_so_user is not None:
                    logging.info(f"User: {l_so_user}")  
               
                if l_event_action is not None:
                    logging.info(f"Event Action: {l_event_action}")  

                if l_host_os_name is not None:
                    logging.info(f"OS Version: {l_host_os_name}")  
                
                if l_source_geo_country_name is not None:
                    logging.info(f"Source Geo Contry: {l_source_geo_country_name}")
                
                if l_environment is not None:
                    logging.info(f"Environment: {l_environment}")
                
                
                if l_tags is not None:
                    logging.info(f"Tags: {l_tags}")
                
                # Build log message with only non-None values
                log_fields = []
                
                # Get rule_name from the query file name (without the .json extension)
                #rule_name = os.path.splitext(query_file)[0]  # Remove the .json extension
                log_fields.append(f"rule_name={rule_name};")  # Add rule_name to log fields
                
                # Include the new event ID
                #new_event_id = manage_event_id()  # Assuming manage_event_id is defined elsewhere
                log_fields.append(f"event.id={new_event_id};")  # Add event.id to log fields

                if l_subscription_id is not None:
                    log_fields.append(f"subscription_id={l_subscription_id};")
                if l_source_ip is not None:
                    log_fields.append(f"source_ip={l_source_ip};")
                if l_event_action is not None:
                    log_fields.append(f"event_action={l_event_action};")
                if l_observer_product is not None:
                    log_fields.append(f"observer_product={l_observer_product};")
                if l_host_os_name is not None:
                    log_fields.append(f"host_os_name={l_host_os_name};")
                if l_source_geo_country_name is not None:
                    log_fields.append(f"source_geo_country_name={l_source_geo_country_name};")
                if l_doc_count is not None:
                    log_fields.append(f"doc_count={l_doc_count};")
                if l_checkpoint_user is not None:
                    log_fields.append(f"checkpoint_user={l_checkpoint_user};")
                if l_so_user is not None:
                    log_fields.append(f"so_user={l_so_user};")
                if l_so_client_version is not None:
                    log_fields.append(f"so_client_version={l_so_client_version};")
                if l_tags is not None:
                    log_fields.append(f"tags={l_tags};")
                # Join log fields into a single string and log it
                if log_fields:
                    log_message = " ".join(log_fields)
                    logging.info(log_message)

                    # Send log message to Netcat
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.connect((nc_host, nc_port))
                            s.sendall(log_message.encode('utf-8'))
                    except Exception as e:
                        logging.error(f"Failed to send log message to Netcat: {e}")


    except subprocess.CalledProcessError as e:
        logging.error(f"Error running curl command for file {query_file}: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON response for file {query_file}: {e}")

