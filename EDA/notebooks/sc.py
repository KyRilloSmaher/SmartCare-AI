# import pandas as pd
# import os

# # 1. Load the full dataset
# # Ensure the path matches your actual file location
# csv_path = "Products.csv"
# output_file = "InsertProducts.sql"

# if not os.path.exists(csv_path):
#     print(f"Error: {csv_path} not found.")
# else:
#     df = pd.read_csv(csv_path)

#     def format_sql_value(val, is_string=True):
#         """Handles NULLs, escaping single quotes, and N'' prefix for SQL."""
#         if pd.isna(val) or str(val).strip().upper() == 'NA':
#             return "NULL"
#         if is_string:
#             # Escape single quotes by doubling them (e.g., Dr. Reddy's -> Dr. Reddy''s)
#             safe_val = str(val).replace("'", "''")
#             return f"N'{safe_val}'"
#         return str(val)

#     def to_bit(val):
#         """Converts True/False strings or booleans to 1/0."""
#         s = str(val).strip().lower()
#         return "1" if s in ['true', '1', '1.0', 'yes'] else "0"

#     # 2. Open file and start writing
#     with open(output_file, "w", encoding="utf-8") as f:
#         f.write("SET NOCOUNT ON;\nGO\n\n")
        
#         for _, row in df.iterrows():
#             # Mapping CSV columns to your specific SQL order:
#             # [ProductId], [NameAr], [NameEn], [CategoryId], [CompanyId], [Description], 
#             # [MedicalDescription], [Tags], [AverageRating], [TotalRatings], [DiscountPercentage], 
#             # [ActiveIngredients], [SideEffects], [Contraindications], [Price], [IsDeleted], 
#             # [IsAvailable], [DosageForm]
            
#             sql = (
#                 f"INSERT INTO [dbo].[Products] ("
#                 f"[ProductId], [NameAr], [NameEn], [CategoryId], [CompanyId], "
#                 f"[Description], [MedicalDescription], [Tags], [AverageRating], [TotalRatings], "
#                 f"[DiscountPercentage], [ActiveIngredients], [SideEffects], [Contraindications], "
#                 f"[Price], [IsDeleted], [IsAvailable], [DosageForm]) "
#                 f"VALUES ("
#                 f"'{row['ProductId']}', "               # ProductId
#                 f"{format_sql_value(row['NameEn'])}, "   # NameAr
#                 f"{format_sql_value(row['NameEn'])}, "   # NameEn
#                 f"'{row['CategoryId']}', "              # CategoryId
#                 f"'{row['CompanyId']}', "               # CompanyId
#                 f"{format_sql_value(row['Description'])}, " 
#                 f"{format_sql_value(row['MedicalDescription'])}, "
#                 f"{format_sql_value(row['Tags'])}, "
#                 f"{row['AverageRating']}, "
#                 f"{row['TotalRatings']}, "
#                 f"{row['DiscountPercentage']}, "
#                 f"{format_sql_value(row['ActiveIngredients'])}, "
#                 f"{format_sql_value(row['SideEffects'])}, "
#                 f"{format_sql_value(row['Contraindications'])}, "
#                 f"{row['Price']}, "
#                 f"{to_bit(row['IsDeleted'])}, "
#                 f"{to_bit(row['IsAvailable'])}, "
#                 f"{format_sql_value(row['DosageForm'])});\n"
#             )
#             f.write(sql)

#     print(f"Success! {len(df)} insert statements have been written to {output_file}")

# import pandas as pd
# import os

# # 1. Load the company dataset
# # (Assuming you are using the company_df we created earlier or a saved CSV)
# csv_path = "Companies.csv" 
# output_file = "InsertCompanies.sql"

# if not os.path.exists(csv_path):
#     print(f"Error: {csv_path} not found. Ensure you have saved your company dataframe to CSV first.")
# else:
#     df = pd.read_csv(csv_path)

#     def format_sql_string(val):
#         """Escapes single quotes and adds N prefix for SQL strings."""
#         if pd.isna(val):
#             return "NULL"
#         # Escape single quotes (e.g., Lowe's -> Lowe''s)
#         safe_val = str(val).replace("'", "''")
#         return f"N'{safe_val}'"

#     # 2. Generate the SQL file
#     with open(output_file, "w", encoding="utf-8") as f:
#         f.write("SET NOCOUNT ON;\nGO\n\n")
        
#         for _, row in df.iterrows():
#             # Mapping columns: Id, Name, LogoUrl, IsDeleted, ProductsCount
#             # Note: IsDeleted is a bit/int, ProductsCount is an int
            
#             sql = (
#                 f"INSERT INTO [dbo].[Company] ([Id], [Name], [LogoUrl], [IsDeleted], [ProductsCount]) "
#                 f"VALUES ("
#                 f"'{row['CompanyId']}', "                # UUIDs usually don't need N prefix
#                 f"{format_sql_string(row['CompanyName'])}, "
#                 f"{format_sql_string(row['LogoUrl'])}, "
#                 f"{int(row['IsDeleted'])}, "       # Convert to 0 or 1
#                 f"{int(row['ProductsCount'])});\n" # Ensure integer
#             )
#             f.write(sql)

#     print(f"Success! {len(df)} company records written to {output_file}")


import pandas as pd
import os

# Define the path to your notebook's CSV
csv_path = r"Product_Images.csv"
output_file = "InsertProductImages_Fixed.sql"

if not os.path.exists(csv_path):
    print(f"Error: Could not find the file at {csv_path}")
else:
    # Use quotechar and skipinitialspace to handle the complex URLs in your CSV
    df = pd.read_csv(csv_path, quotechar='"', skipinitialspace=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("SET NOCOUNT ON;\nGO\n\n")
        
        count = 0
        for index, row in df.iterrows():
            try:
                # 1. Extract and Clean values
                # Mapping: CSV(Id, ProductId, IsPrimary, Url) -> SQL([Id], [Url], [IsPrimary], [ProductId])
                img_id = str(row['Id']).strip()
                prod_id = str(row['ProductId']).strip()
                url = str(row['Url']).replace("'", "''").strip() # Escape single quotes in URLs
                
                # Convert 'True'/'False' to 1/0
                is_primary = 1 if str(row['IsPrimary']).strip().lower() == 'true' else 0

                # 2. Build the statement with correct column order
                # SQL expects: [Id], [Url], [IsPrimary], [ProductId]
                sql = (
                    f"INSERT INTO [dbo].[ProductImage] ([Id], [Url], [IsPrimary], [ProductId]) "
                    f"VALUES ('{img_id}', N'{url}', {is_primary}, '{prod_id}');\n"
                )
                
                f.write(sql)
                count += 1
            except Exception as e:
                print(f"Skipping row {index} due to error: {e}")

    print(f"Finished! {count} SQL statements written to {output_file}")