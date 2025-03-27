from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv
import os
import logging
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class Database:
    """PostgreSQL database connection and operations handler."""
    
    def __init__(self):
        """Initialize database connection from environment variables."""
        # Get database credentials from environment
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.host = os.getenv('DB_HOST')
        self.port = os.getenv('DB_PORT')
        self.database = os.getenv('DB_DATABASE')
        
        # Connection string
        connection_string = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        logger.info(f"Connecting to database: postgresql://{self.user}:****@{self.host}:{self.port}/{self.database}")
        
        # Create engine
        self.engine = create_engine(connection_string)
        
        # Test connection
        try:
            with self.engine.connect() as conn:
                logger.info("Successfully connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise

    def parse_table_name(self, table_name):
        """
        Parse a table name that may include schema (e.g., 'schema.table' or 'public.schema.table')
        
        Args:
            table_name (str): Table name, possibly including schema
            
        Returns:
            tuple: (schema, table_only) - Parsed schema and table name
        """
        schema = 'public'  # Default schema
        table_only = table_name
        
        if '.' in table_name:
            parts = table_name.split('.')
            if len(parts) == 2:
                schema, table_only = parts
            elif len(parts) == 3:
                # Format: "public.schema.table" or similar
                _, schema, table_only = parts
                
        return schema, table_only

    def get_schemas(self):
        """Get all schema names from database."""
        inspector = inspect(self.engine)
        return inspector.get_schema_names()

    def get_tables(self, schema='public'):
        """
        Get all table names from a specific schema.
        
        Args:
            schema (str): Schema name to get tables from
            
        Returns:
            list: List of table names in schema
        """
        inspector = inspect(self.engine)
        return inspector.get_table_names(schema=schema)
    
    def get_table_data(self, table_name, limit=None):
        """
        Get data from a specific table.
        
        Args:
            table_name (str): Name of the table to get data from
        
        Returns:
            pandas.DataFrame: DataFrame containing table data
        """
        if limit is not None:
            query = f"SELECT * FROM {table_name} LIMIT {limit}" 
        else:
            query = f"SELECT * FROM {table_name}"
        return pd.read_sql_query(query, self.engine)
    
    
    def check_table_exists(self, schema, table_name):
        """
        Check if a table exists in the specified schema.
        
        Args:
            schema (str): Schema name
            table_name (str): Table name without schema prefix
            
        Returns:
            bool: True if table exists, False otherwise
        """
        inspector = inspect(self.engine)
        return table_name in inspector.get_table_names(schema=schema)
    
    def store_data(self, df, table_name, primary_key='post_id'):
        """
        Store dataframe in PostgreSQL with primary key constraint to avoid duplicates.
        
        Args:
            df (pandas.DataFrame): DataFrame to store
            table_name (str): Name of the table to store data in (can include schema like 'schema.table')
            primary_key (str): Column name to use as primary key
            
        Returns:
            bool: Success status
        """
        if df is None or df.empty:
            logger.warning("Empty DataFrame provided, nothing to store")
            return False
            
        # Verify primary key exists in dataframe
        if primary_key not in df.columns:
            logger.error(f"Primary key column '{primary_key}' not found in dataframe")
            return False
        
        # Parse schema and table name
        schema, table_only = self.parse_table_name(table_name)
        
        # Create unique name for temporary table
        temp_table = f"temp_{table_only}"
        
        try:
            # Check if table exists
            if not self.check_table_exists(schema, table_only):
                logger.error(f"Table {schema}.{table_only} does not exist")
                return False
            
            logger.info(f"Table {schema}.{table_only} exists, proceeding with upsert operation")
            
            # Create temporary table in the appropriate schema
            df.to_sql(temp_table, self.engine, schema=schema, if_exists='replace', index=False)
            logger.info(f"Created temporary table {schema}.{temp_table}")
            
            # Use a single SQL statement for the upsert operation
            with self.engine.connect() as connection:
                # Create the update part of the query for all columns except primary key
                update_columns = ', '.join([f"{col} = EXCLUDED.{col}" for col in df.columns if col != primary_key])
                
                # Full qualified names for tables
                qualified_table = f"{schema}.{table_only}"
                qualified_temp = f"{schema}.{temp_table}"
                
                # Execute the upsert
                upsert_query = text(f"""
                INSERT INTO {qualified_table} 
                SELECT * FROM {qualified_temp}
                ON CONFLICT ({primary_key}) 
                DO UPDATE SET {update_columns}
                """)
                
                connection.execute(upsert_query)
                logger.info(f"Executed upsert operation on {qualified_table}")
                
                # Clean up by dropping temporary table
                connection.execute(text(f"DROP TABLE IF EXISTS {qualified_temp}"))
                connection.commit()
                
                logger.info(f"Successfully inserted/updated {len(df)} rows in table {qualified_table}")
                return True
                
        except Exception as e:
            logger.error(f"Error storing data: {e}")
            # Clean up temporary table if an error occurs
            try:
                with self.engine.connect() as cleanup_connection:
                    qualified_temp = f"{schema}.{temp_table}"
                    cleanup_connection.execute(text(f"DROP TABLE IF EXISTS {qualified_temp}"))
                    cleanup_connection.commit()
                    logger.info(f"Cleaned up temporary table {qualified_temp}")
            except Exception as cleanup_error:
                logger.error(f"Error cleaning up temporary table: {cleanup_error}")
            
            return False

if __name__ == "__main__":
    # Example usage
    db = Database()
    df = db.get_table_data('bronze_reddit_reviews')
    logger.info(f"Data: {df}")




