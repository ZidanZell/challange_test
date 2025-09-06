from flask import Flask, request, Response
import json
from function.database_handler import DatabaseManager
from function.help import generate_node_id, get_current_timestamp

app = Flask(__name__)

db = DatabaseManager()
db.initialize_database()

def create_response(status, message, data=None):
    if data is not None:
        response_data = {
            "status": status,
            "message": message,
            "data": data
        }
    else:
        response_data = {
            "status": status,
            "message": message
        }
    
    json_str = json.dumps(response_data, indent=2, ensure_ascii=False)
    return Response(json_str, mimetype='application/json')

class NodeController:
    @staticmethod
    def get_all_nodes():
        query = "SELECT id as node_id, name, updated_at as update_at FROM nodeDB ORDER BY updated_at DESC"
        nodes = db.execute_query(query)
        
        if nodes:
            for node in nodes:
                node['total_sensor'] = 0
                if hasattr(node['update_at'], 'strftime'):
                    node['update_at'] = node['update_at'].strftime("%Y-%m-%d %H:%M:%S")
            return nodes
        return []
    
    @staticmethod
    def create_node(name):
        node_id = generate_node_id()
        updated_at = get_current_timestamp()
        
        query = "INSERT INTO nodeDB (id, name, updated_at) VALUES (%s, %s, %s)"
        result = db.execute_query(query, (node_id, name, updated_at))
        
        if result and result > 0:
            return True, "Node created successfully", NodeController.get_all_nodes()
        return False, "Failed to create node", None
    
    @staticmethod
    def update_node(node_id, name):
        updated_at = get_current_timestamp()
        
        query = "UPDATE nodeDB SET name = %s, updated_at = %s WHERE id = %s"
        result = db.execute_query(query, (name, updated_at, node_id))
        
        if result and result > 0:
            return True, "Node updated successfully", NodeController.get_all_nodes()
        return False, "Failed to update node or node not found", None
    
    @staticmethod
    def delete_node(node_id):
        query = "DELETE FROM nodeDB WHERE id = %s"
        result = db.execute_query(query, (node_id,))
        
        if result and result > 0:
            return True, "Node deleted successfully", NodeController.get_all_nodes()
        return False, "Failed to delete node or node not found", None

@app.route('/api/read/node', methods=['GET'])
def read_nodes():
    try:
        nodes = NodeController.get_all_nodes()
        message = f"Found {len(nodes)} nodes" if nodes else "No nodes found"
        return create_response("Success", message, nodes)
    except Exception as e:
        return create_response("Failed", f"Error: {str(e)}"), 500

@app.route('/api/create/node', methods=['POST'])
def create_node():
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return create_response("Failed", "Name is required"), 400
        
        success, message, nodes = NodeController.create_node(data['name'])
        
        if success:
            return create_response("Success", message, nodes)
        else:
            return create_response("Failed", message), 400
            
    except Exception as e:
        return create_response("Failed", f"Error: {str(e)}"), 500

@app.route('/api/update/node', methods=['PUT'])
def update_node():
    try:
        data = request.get_json()
        
        if not data or 'node_id' not in data or 'name' not in data:
            return create_response("Failed", "Node ID and name are required"), 400
        
        success, message, nodes = NodeController.update_node(data['node_id'], data['name'])
        
        if success:
            return create_response("Success", message, nodes)
        else:
            return create_response("Failed", message), 400
            
    except Exception as e:
        return create_response("Failed", f"Error: {str(e)}"), 500

@app.route('/api/delete/node', methods=['DELETE'])
def delete_node():
    try:
        data = request.get_json()
        
        if not data or 'id' not in data:
            return create_response("Failed", "Node ID is required"), 400
        
        success, message, nodes = NodeController.delete_node(data['id'])
        
        if success:
            return create_response("Success", message, nodes)
        else:
            return create_response("Failed", message), 400
            
    except Exception as e:
        return create_response("Failed", f"Error: {str(e)}"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)