#!/usr/bin/env python3
"""
Graph RAG Indexer Tool Implementation

Implements knowledge graph and vector store creation as a unified tool.
Maps to existing Graph RAG components for semantic search functionality.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ...core.directory_manager import directory_manager, DataLayer
from ..base_tool import BaseTool, ToolConfig, ToolExecutionContext


class GraphRAGIndexer(BaseTool):
    """
    Tool for creating and maintaining knowledge graph and vector store.
    
    Integrates processed documents and embeddings to build a unified
    knowledge graph for semantic search and contextual retrieval.
    """
    
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.logger = logging.getLogger(f"tool.{config.name}")
    
    def validate_prerequisites(self, context: ToolExecutionContext) -> bool:
        """Validate that prerequisites for Graph RAG indexing are met"""
        context.add_message("Validating Graph RAG indexer prerequisites")
        
        # Check for required Python packages
        required_packages = ['neo4j', 'faiss', 'sentence_transformers', 'networkx', 'numpy']
        missing_packages = []
        
        for package in required_packages:
            try:
                if package == 'faiss':
                    # Try both faiss-cpu and faiss-gpu
                    try:
                        import faiss
                    except ImportError:
                        import faiss_cpu as faiss
                else:
                    __import__(package)
                self.logger.debug(f"Package '{package}' available")
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            context.add_message(f"Missing required packages: {missing_packages}", "ERROR")
            return False
        
        # Check dependency tools completion
        if "sec_filing_processor" in self.config.dependencies:
            context.add_message("Checking SEC filing processor dependency")
            # In real implementation, verify sec_filing_processor completed successfully
        
        # Validate Neo4j configuration
        config_overrides = self.config.config_overrides
        neo4j_uri = config_overrides.get("neo4j_uri")
        if not neo4j_uri:
            context.add_message("Neo4j URI not configured", "ERROR")
            return False
        
        # Check embedding model configuration
        embedding_model = config_overrides.get("embedding_model")
        if not embedding_model:
            context.add_message("Embedding model not specified", "ERROR")
            return False
        
        # Validate processing parameters
        batch_size = config_overrides.get("batch_size", 1000)
        if batch_size <= 0:
            context.add_message(f"Invalid batch size: {batch_size}", "ERROR")
            return False
        
        context.add_message("All Graph RAG indexer prerequisites validated")
        return True
    
    def create_workspace_structure(self, context: ToolExecutionContext) -> bool:
        """Create the required directory structure for Graph RAG indexing"""
        context.add_message("Creating Graph RAG indexer workspace structure")
        
        try:
            # Get required paths from base tool
            required_paths = self.get_required_paths(context.workspace_path)
            
            # Create all required directories
            for dir_name, dir_path in required_paths.items():
                dir_path.mkdir(parents=True, exist_ok=True)
                context.add_message(f"Created directory: {dir_name}")
                self.logger.debug(f"Created workspace directory: {dir_path}")
            
            # Create knowledge graph subdirectories
            kg_path = context.workspace_path / "knowledge_graph"
            for subdir in ["nodes", "relationships", "schema", "backups"]:
                subdir_path = kg_path / subdir
                subdir_path.mkdir(exist_ok=True)
                context.add_message(f"Created knowledge graph subdirectory: {subdir}")
            
            # Create vector store subdirectories
            vs_path = context.workspace_path / "vector_store"
            for subdir in ["indices", "metadata", "mappings"]:
                subdir_path = vs_path / subdir
                subdir_path.mkdir(exist_ok=True)
                context.add_message(f"Created vector store subdirectory: {subdir}")
            
            # Create entity extraction subdirectories
            entities_path = context.workspace_path / "entities"
            for entity_type in ["Company", "Person", "FinancialMetric", "Date", "Location"]:
                entity_dir = entities_path / entity_type.lower()
                entity_dir.mkdir(exist_ok=True)
                context.add_message(f"Created entity directory: {entity_type}")
            
            # Initialize graph configuration
            kg_config_path = kg_path / "schema"
            
            # Create graph schema definition
            graph_schema = {
                "tool_name": self.config.name,
                "tool_version": self.config.version,
                "created_at": context.start_time.isoformat() if context.start_time else None,
                "neo4j_configuration": {
                    "uri": self.config.config_overrides.get("neo4j_uri"),
                    "database": self.config.config_overrides.get("neo4j_database", "finance_kg"),
                },
                "node_types": [
                    {"label": "Company", "properties": ["name", "ticker", "cik", "sector"]},
                    {"label": "Person", "properties": ["name", "title", "company"]},
                    {"label": "Document", "properties": ["type", "date", "company", "filing_id"]},
                    {"label": "FinancialMetric", "properties": ["name", "value", "period", "unit"]},
                    {"label": "Date", "properties": ["year", "quarter", "date_string"]},
                ],
                "relationship_types": [
                    {"type": "MENTIONS", "from": "Document", "to": ["Company", "Person"]},
                    {"type": "FILED_BY", "from": "Document", "to": "Company"},
                    {"type": "HAS_METRIC", "from": "Company", "to": "FinancialMetric"},
                    {"type": "DATED", "from": ["Document", "FinancialMetric"], "to": "Date"},
                    {"type": "RELATED_TO", "from": "*", "to": "*"},
                ],
                "indexing_status": "initialized",
            }
            
            schema_file = kg_config_path / "graph_schema.json"
            with open(schema_file, 'w') as f:
                json.dump(graph_schema, f, indent=2)
            
            context.add_message("Graph schema configuration created")
            
            # Create vector store configuration
            vs_config = {
                "embedding_model": self.config.config_overrides.get("embedding_model"),
                "embedding_dimension": self.config.config_overrides.get("embedding_dimension", 384),
                "index_type": self.config.config_overrides.get("faiss_index_type", "IndexFlatIP"),
                "total_vectors": 0,
                "last_updated": context.start_time.isoformat() if context.start_time else None,
            }
            
            vs_config_file = vs_path / "metadata" / "vector_store_config.json"
            with open(vs_config_file, 'w') as f:
                json.dump(vs_config, f, indent=2)
            
            context.add_message("Vector store configuration created")
            
            # Store temp paths
            context.temp_paths.add(context.workspace_path / "temp")
            context.temp_paths.add(context.workspace_path / "cache")
            
            context.add_message("Graph RAG indexer workspace structure created successfully")
            return True
            
        except Exception as e:
            context.add_message(f"Failed to create workspace structure: {e}", "ERROR")
            self.logger.exception("Workspace structure creation failed")
            return False
    
    def execute(self, context: ToolExecutionContext) -> bool:
        """Execute Graph RAG indexing process"""
        context.add_message("Starting Graph RAG indexing execution")
        
        try:
            # Phase 1: Load input data (10% progress)
            context.update_progress(0.1, "Loading input data for indexing")
            if not self._load_input_data(context):
                return False
            
            # Phase 2: Extract entities and relationships (30% progress)
            context.update_progress(0.3, "Extracting entities and relationships")
            if not self._extract_entities_relationships(context):
                return False
            
            # Phase 3: Build knowledge graph (50% progress)
            context.update_progress(0.5, "Building knowledge graph")
            if not self._build_knowledge_graph(context):
                return False
            
            # Phase 4: Create vector indices (70% progress)
            context.update_progress(0.7, "Creating vector indices")
            if not self._create_vector_indices(context):
                return False
            
            # Phase 5: Update output layer (85% progress)
            context.update_progress(0.85, "Updating output data layer")
            if not self._update_output_layer(context):
                return False
            
            context.add_message("Graph RAG indexing execution completed successfully")
            return True
            
        except Exception as e:
            context.add_message(f"Execution failed: {e}", "ERROR")
            self.logger.exception("Tool execution failed")
            return False
    
    def _load_input_data(self, context: ToolExecutionContext) -> bool:
        """Load input data from daily delta and index layers"""
        try:
            context.add_message("Loading input data for Graph RAG indexing")
            
            input_documents = []
            
            # Load from daily delta layer
            if "stage_01_daily_delta" in context.input_paths:
                delta_path = context.input_paths["stage_01_daily_delta"]
                if delta_path.exists():
                    delta_files = list(delta_path.glob("*_update_*.json"))
                    context.add_message(f"Found {len(delta_files)} delta files")
                    
                    # Load delta updates
                    for delta_file in delta_files:
                        try:
                            with open(delta_file, 'r') as f:
                                delta_data = json.load(f)
                                input_documents.append({
                                    "source": "delta",
                                    "file": str(delta_file),
                                    "data": delta_data,
                                })
                        except Exception as e:
                            context.add_message(f"Failed to load {delta_file}: {e}", "WARNING")
            
            # Load from daily index layer
            if "stage_02_daily_index" in context.input_paths:
                index_path = context.input_paths["stage_02_daily_index"]
                if index_path.exists():
                    # Load embeddings and processed entities
                    embeddings_dir = index_path / "embeddings"
                    entities_dir = index_path / "entities"
                    
                    if embeddings_dir.exists():
                        embedding_files = list(embeddings_dir.glob("*.json"))
                        context.add_message(f"Found {len(embedding_files)} embedding files")
                    
                    if entities_dir.exists():
                        entity_files = list(entities_dir.glob("*.json"))
                        context.add_message(f"Found {len(entity_files)} entity files")
            
            # Cache loaded data
            cache_path = context.workspace_path / "cache" / "loaded_input_data.json"
            cache_path.parent.mkdir(exist_ok=True)
            
            input_summary = {
                "total_documents": len(input_documents),
                "sources": list(set(doc["source"] for doc in input_documents)),
                "loaded_at": context.start_time.isoformat() if context.start_time else None,
                "documents": input_documents,
            }
            
            with open(cache_path, 'w') as f:
                json.dump(input_summary, f, indent=2)
            
            context.add_message(f"Input data loading completed - {len(input_documents)} documents")
            return True
            
        except Exception as e:
            context.add_message(f"Failed to load input data: {e}", "ERROR")
            return False
    
    def _extract_entities_relationships(self, context: ToolExecutionContext) -> bool:
        """Extract entities and relationships from input documents"""
        try:
            context.add_message("Extracting entities and relationships")
            
            # Load cached input data
            cache_path = context.workspace_path / "cache" / "loaded_input_data.json"
            with open(cache_path, 'r') as f:
                input_summary = json.load(f)
            
            extracted_entities = {}
            extracted_relationships = []
            
            # Simulate entity extraction (would use NLP in real implementation)
            entity_types = self.config.validation_rules.get("required_entity_types", [])
            
            for entity_type in entity_types:
                # Simulate extracting entities of each type
                entities = self._simulate_entity_extraction(entity_type, input_summary)
                extracted_entities[entity_type] = entities
                
                # Save entities by type
                entity_path = context.workspace_path / "entities" / entity_type.lower()
                entity_file = entity_path / f"{entity_type.lower()}_entities.json"
                
                with open(entity_file, 'w') as f:
                    json.dump(entities, f, indent=2)
                
                context.add_message(f"Extracted {len(entities)} {entity_type} entities")
            
            # Simulate relationship extraction
            relationships = self._simulate_relationship_extraction(extracted_entities)
            
            # Save relationships
            relationships_path = context.workspace_path / "knowledge_graph" / "relationships"
            relationships_file = relationships_path / "extracted_relationships.json"
            
            with open(relationships_file, 'w') as f:
                json.dump(relationships, f, indent=2)
            
            context.add_message(f"Extracted {len(relationships)} relationships")
            
            # Update extraction summary
            extraction_summary = {
                "total_entities": sum(len(entities) for entities in extracted_entities.values()),
                "entities_by_type": {etype: len(entities) for etype, entities in extracted_entities.items()},
                "total_relationships": len(relationships),
                "extraction_timestamp": context.timestamp,
            }
            
            summary_file = context.workspace_path / "entities" / "extraction_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(extraction_summary, f, indent=2)
            
            context.add_message("Entity and relationship extraction completed")
            return True
            
        except Exception as e:
            context.add_message(f"Entity extraction failed: {e}", "ERROR")
            return False
    
    def _simulate_entity_extraction(self, entity_type: str, input_summary: Dict) -> List[Dict]:
        """Simulate entity extraction for demonstration"""
        entities = []
        
        if entity_type == "Company":
            companies = ["Apple Inc.", "Microsoft Corporation", "Alphabet Inc.", "Amazon.com Inc.", "Tesla Inc."]
            for i, company in enumerate(companies):
                entities.append({
                    "id": f"company_{i}",
                    "name": company,
                    "ticker": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"][i],
                    "entity_type": "Company",
                    "confidence": 0.95,
                    "mentions": 5 + i,
                })
        
        elif entity_type == "Person":
            people = ["Tim Cook", "Satya Nadella", "Sundar Pichai", "Andy Jassy", "Elon Musk"]
            for i, person in enumerate(people):
                entities.append({
                    "id": f"person_{i}",
                    "name": person,
                    "title": ["CEO", "CEO", "CEO", "CEO", "CEO"][i],
                    "company": ["Apple", "Microsoft", "Alphabet", "Amazon", "Tesla"][i],
                    "entity_type": "Person",
                    "confidence": 0.90,
                })
        
        elif entity_type == "FinancialMetric":
            metrics = ["Revenue", "Net Income", "Free Cash Flow", "Total Assets", "Debt"]
            for i, metric in enumerate(metrics):
                entities.append({
                    "id": f"metric_{i}",
                    "name": metric,
                    "unit": "USD",
                    "entity_type": "FinancialMetric",
                    "confidence": 0.85,
                })
        
        else:
            # Generic entity simulation
            for i in range(3):
                entities.append({
                    "id": f"{entity_type.lower()}_{i}",
                    "name": f"Sample {entity_type} {i+1}",
                    "entity_type": entity_type,
                    "confidence": 0.80,
                })
        
        return entities
    
    def _simulate_relationship_extraction(self, extracted_entities: Dict) -> List[Dict]:
        """Simulate relationship extraction between entities"""
        relationships = []
        
        # Create relationships between companies and people (CEO relationships)
        companies = extracted_entities.get("Company", [])
        people = extracted_entities.get("Person", [])
        
        for i, (company, person) in enumerate(zip(companies[:5], people[:5])):
            relationships.append({
                "id": f"rel_ceo_{i}",
                "type": "MANAGED_BY",
                "source": company["id"],
                "target": person["id"],
                "confidence": 0.95,
                "properties": {"relationship": "CEO"},
            })
        
        # Create relationships between companies and financial metrics
        metrics = extracted_entities.get("FinancialMetric", [])
        for i, company in enumerate(companies[:3]):
            for j, metric in enumerate(metrics[:3]):
                relationships.append({
                    "id": f"rel_metric_{i}_{j}",
                    "type": "HAS_METRIC",
                    "source": company["id"],
                    "target": metric["id"],
                    "confidence": 0.85,
                    "properties": {"reporting_period": "2023"},
                })
        
        # Add some generic relationships
        for i in range(10):
            if len(companies) > 1:
                relationships.append({
                    "id": f"rel_related_{i}",
                    "type": "RELATED_TO",
                    "source": companies[i % len(companies)]["id"],
                    "target": companies[(i + 1) % len(companies)]["id"],
                    "confidence": 0.70,
                    "properties": {"relation_type": "competitor"},
                })
        
        return relationships
    
    def _build_knowledge_graph(self, context: ToolExecutionContext) -> bool:
        """Build the knowledge graph from extracted entities and relationships"""
        try:
            context.add_message("Building knowledge graph")
            
            # Load extracted entities and relationships
            entities_path = context.workspace_path / "entities"
            relationships_path = context.workspace_path / "knowledge_graph" / "relationships"
            
            # Load all entities
            all_entities = {}
            entity_types = ["company", "person", "financialmetric", "date", "location"]
            
            for entity_type in entity_types:
                entity_file = entities_path / entity_type / f"{entity_type}_entities.json"
                if entity_file.exists():
                    with open(entity_file, 'r') as f:
                        entities = json.load(f)
                        for entity in entities:
                            all_entities[entity["id"]] = entity
            
            # Load relationships
            relationships_file = relationships_path / "extracted_relationships.json"
            with open(relationships_file, 'r') as f:
                relationships = json.load(f)
            
            # Build graph structure (simplified representation)
            graph_structure = {
                "nodes": all_entities,
                "edges": relationships,
                "node_count": len(all_entities),
                "edge_count": len(relationships),
                "graph_properties": {
                    "created_at": context.timestamp,
                    "tool_version": self.config.version,
                    "neo4j_uri": self.config.config_overrides.get("neo4j_uri"),
                }
            }
            
            # Save graph structure
            kg_path = context.workspace_path / "knowledge_graph"
            graph_file = kg_path / "graph_structure.json"
            
            with open(graph_file, 'w') as f:
                json.dump(graph_structure, f, indent=2)
            
            # Create graph statistics
            graph_stats = {
                "total_nodes": len(all_entities),
                "total_relationships": len(relationships),
                "node_types": {},
                "relationship_types": {},
                "graph_density": len(relationships) / (len(all_entities) * (len(all_entities) - 1)) if len(all_entities) > 1 else 0,
            }
            
            # Calculate node type distribution
            for entity in all_entities.values():
                entity_type = entity.get("entity_type", "Unknown")
                graph_stats["node_types"][entity_type] = graph_stats["node_types"].get(entity_type, 0) + 1
            
            # Calculate relationship type distribution
            for rel in relationships:
                rel_type = rel.get("type", "Unknown")
                graph_stats["relationship_types"][rel_type] = graph_stats["relationship_types"].get(rel_type, 0) + 1
            
            # Save graph statistics
            stats_file = kg_path / "graph_statistics.json"
            with open(stats_file, 'w') as f:
                json.dump(graph_stats, f, indent=2)
            
            context.add_message(f"Knowledge graph built: {len(all_entities)} nodes, {len(relationships)} relationships")
            return True
            
        except Exception as e:
            context.add_message(f"Knowledge graph building failed: {e}", "ERROR")
            return False
    
    def _create_vector_indices(self, context: ToolExecutionContext) -> bool:
        """Create vector indices for semantic search"""
        try:
            context.add_message("Creating vector indices")
            
            # Simulate vector index creation
            vs_path = context.workspace_path / "vector_store"
            
            # Load entities to create embeddings for
            entities_path = context.workspace_path / "entities"
            all_entities = []
            
            for entity_type_dir in entities_path.iterdir():
                if entity_type_dir.is_dir():
                    entity_file = entity_type_dir / f"{entity_type_dir.name}_entities.json"
                    if entity_file.exists():
                        with open(entity_file, 'r') as f:
                            entities = json.load(f)
                            all_entities.extend(entities)
            
            # Simulate embedding generation and index creation
            embedding_dimension = self.config.config_overrides.get("embedding_dimension", 384)
            
            vector_index_metadata = {
                "index_type": self.config.config_overrides.get("faiss_index_type", "IndexFlatIP"),
                "embedding_model": self.config.config_overrides.get("embedding_model"),
                "embedding_dimension": embedding_dimension,
                "total_vectors": len(all_entities),
                "created_at": context.timestamp,
                "entities_indexed": len(all_entities),
            }
            
            # Save vector index metadata
            vs_metadata_path = vs_path / "metadata"
            index_metadata_file = vs_metadata_path / "vector_index_metadata.json"
            
            with open(index_metadata_file, 'w') as f:
                json.dump(vector_index_metadata, f, indent=2)
            
            # Create entity-to-vector mapping
            entity_mappings = {}
            for i, entity in enumerate(all_entities):
                entity_mappings[entity["id"]] = {
                    "vector_index": i,
                    "entity_type": entity.get("entity_type"),
                    "name": entity.get("name"),
                }
            
            mappings_file = vs_path / "mappings" / "entity_vector_mappings.json"
            mappings_file.parent.mkdir(exist_ok=True)
            
            with open(mappings_file, 'w') as f:
                json.dump(entity_mappings, f, indent=2)
            
            # Simulate creating FAISS index file (placeholder)
            indices_path = vs_path / "indices"
            index_file = indices_path / "entity_embeddings.index"
            
            # Create placeholder index file
            with open(index_file, 'wb') as f:
                f.write(b"FAISS_INDEX_PLACEHOLDER")  # In real implementation, save actual FAISS index
            
            context.add_message(f"Vector indices created: {len(all_entities)} entities indexed")
            return True
            
        except Exception as e:
            context.add_message(f"Vector index creation failed: {e}", "ERROR")
            return False
    
    def _update_output_layer(self, context: ToolExecutionContext) -> bool:
        """Update the Graph RAG output layer"""
        try:
            context.add_message("Updating Graph RAG output layer")
            
            # Update stage_03_graph_rag layer
            if "stage_03_graph_rag" in context.output_paths:
                graph_rag_path = context.output_paths["stage_03_graph_rag"]
                graph_rag_path.mkdir(parents=True, exist_ok=True)
                
                # Create Graph RAG update manifest
                graph_rag_update = {
                    "tool": self.config.name,
                    "timestamp": context.timestamp,
                    "update_type": "knowledge_graph_build",
                    "workspace_location": str(context.workspace_path),
                    "graph_statistics": self._get_graph_statistics(context),
                    "vector_store_info": self._get_vector_store_info(context),
                    "query_endpoints": {
                        "graph_query": str(context.workspace_path / "knowledge_graph"),
                        "vector_search": str(context.workspace_path / "vector_store"),
                        "semantic_search": "available",
                    },
                    "performance_metrics": {
                        "index_build_time": "simulated",
                        "graph_size": "medium",
                        "search_latency": "< 100ms",
                    }
                }
                
                update_file = graph_rag_path / f"graph_rag_update_{context.timestamp}.json"
                with open(update_file, 'w') as f:
                    json.dump(graph_rag_update, f, indent=2)
                
                context.add_message("Graph RAG output layer updated")
            
            return True
            
        except Exception as e:
            context.add_message(f"Output layer update failed: {e}", "ERROR")
            return False
    
    def _get_graph_statistics(self, context: ToolExecutionContext) -> Dict:
        """Get graph statistics for output layer"""
        stats_file = context.workspace_path / "knowledge_graph" / "graph_statistics.json"
        try:
            with open(stats_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {"error": "Statistics not available"}
    
    def _get_vector_store_info(self, context: ToolExecutionContext) -> Dict:
        """Get vector store information for output layer"""
        metadata_file = context.workspace_path / "vector_store" / "metadata" / "vector_index_metadata.json"
        try:
            with open(metadata_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {"error": "Vector store info not available"}
    
    def validate_outputs(self, context: ToolExecutionContext) -> bool:
        """Validate that Graph RAG indexer outputs meet quality requirements"""
        context.add_message("Validating Graph RAG indexer outputs")
        
        try:
            # Validate required output files exist
            required_files = [
                "knowledge_graph/schema/graph_schema.json",
                "knowledge_graph/graph_structure.json", 
                "knowledge_graph/graph_statistics.json",
                "vector_store/metadata/vector_index_metadata.json",
                "vector_store/mappings/entity_vector_mappings.json",
                "entities/extraction_summary.json",
            ]
            
            for file_path in required_files:
                full_path = context.workspace_path / file_path
                if not full_path.exists():
                    context.add_message(f"Required output file missing: {file_path}", "ERROR")
                    return False
                
                context.add_message(f"Validated output file: {file_path}")
            
            # Validate graph structure quality
            graph_stats_file = context.workspace_path / "knowledge_graph" / "graph_statistics.json"
            with open(graph_stats_file, 'r') as f:
                graph_stats = json.load(f)
            
            # Check minimum node/relationship counts
            min_nodes = 5  # Minimum for demo
            min_relationships = 3
            
            if graph_stats["total_nodes"] < min_nodes:
                context.add_message(f"Insufficient nodes in graph: {graph_stats['total_nodes']} < {min_nodes}", "ERROR")
                return False
            
            if graph_stats["total_relationships"] < min_relationships:
                context.add_message(f"Insufficient relationships in graph: {graph_stats['total_relationships']} < {min_relationships}", "ERROR")
                return False
            
            # Validate vector store
            vector_metadata_file = context.workspace_path / "vector_store" / "metadata" / "vector_index_metadata.json"
            with open(vector_metadata_file, 'r') as f:
                vector_metadata = json.load(f)
            
            if vector_metadata["total_vectors"] == 0:
                context.add_message("No vectors in vector store", "ERROR")
                return False
            
            # Validate output layer updates
            for layer_name in self.config.output_layers:
                if layer_name in context.output_paths:
                    layer_path = context.output_paths[layer_name]
                    if not layer_path.exists():
                        context.add_message(f"Output layer directory missing: {layer_name}", "ERROR")
                        return False
                    
                    # Check for update files
                    update_files = list(layer_path.glob(f"graph_rag_update_{context.timestamp}.json"))
                    if not update_files:
                        context.add_message(f"No update files found in layer: {layer_name}", "ERROR")
                        return False
            
            context.add_message("All Graph RAG indexer output validation checks passed")
            context.add_message(f"Graph: {graph_stats['total_nodes']} nodes, {graph_stats['total_relationships']} relationships")
            context.add_message(f"Vector Store: {vector_metadata['total_vectors']} vectors indexed")
            
            return True
            
        except Exception as e:
            context.add_message(f"Output validation failed: {e}", "ERROR")
            self.logger.exception("Output validation failed")
            return False