import pandas as pd
import zstandard as zstd
import os
import io

# Set paths
base_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(base_dir, "lichess_db_puzzle.csv.zst")
output_file = os.path.join(base_dir, "filtered_puzzles.csv.zst")

# Set filtering criteria
min_rating = 1000
max_rating = 2300
popularity_threshold = 0.93  # Popularidade mínima

def filter_puzzles_zst(input_file, output_file, min_rating, max_rating, popularity_threshold):
    print("[INFO] Loading and filtering the puzzles...")

    # Open and decompress the input .zst file
    with open(input_file, "rb") as file:
        dctx = zstd.ZstdDecompressor()
        with dctx.stream_reader(file) as reader:
            # Read the data as a DataFrame and handle large files properly
            chunk_size = 100000  # Adjust as needed to avoid memory issues
            filtered_chunks = []

            for chunk in pd.read_csv(reader, chunksize=chunk_size, low_memory=False):
                # Remove any leading/trailing spaces from column names
                chunk.columns = chunk.columns.str.strip()

                # Verify column names (this will help if there's a mismatch)
                if 'Rating' not in chunk.columns or 'Popularity' not in chunk.columns:
                    raise ValueError("[ERROR] 'Rating' or 'Popularity' column not found. Check the CSV structure.")

                # Filter puzzles based on rating and popularity
                filtered_chunk = chunk[
                    (chunk['Rating'] >= min_rating) & 
                    (chunk['Rating'] <= max_rating) & 
                    (chunk['Popularity'] >= popularity_threshold * 100)  # Popularidade no formato 0-100
                ]
                filtered_chunks.append(filtered_chunk)

    # Concatenate filtered chunks
    if filtered_chunks:
        filtered_df = pd.concat(filtered_chunks)

        # Write the filtered DataFrame to an in-memory buffer (StringIO)
        with io.StringIO() as csv_buffer:
            filtered_df.to_csv(csv_buffer, index=False)
            
            # Convert the CSV string to bytes
            csv_bytes = csv_buffer.getvalue().encode('utf-8')

        # Compress and write to the .zst file
        with open(output_file, "wb") as f_out:
            cctx = zstd.ZstdCompressor(level=3)
            f_out.write(cctx.compress(csv_bytes))
        
        print(f"[INFO] Successfully saved {len(filtered_df)} filtered puzzles to {output_file}.")
    else:
        print("[INFO] No puzzles found in the specified rating or popularity range.")

if __name__ == "__main__":
    filter_puzzles_zst(input_file, output_file, min_rating, max_rating, popularity_threshold)
