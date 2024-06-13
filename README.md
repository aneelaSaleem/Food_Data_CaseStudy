## Open Food Facts Data Processor

This project gets product events from [Food Data](!https://world.openfoodfacts.org/api/v0/product) and save into postgress db.

### How to run?

#### From local machine
It's very simple to run from local machine. I tested it on mac. I hope it works on other operating systems too. 
You have to follow these steps:
1. You should modify .env file with appropriate values
2. Setup environment using `make setup` command
3. Check python style using `make lint`
4. Run tests python `make test`
5. Execute program `make run`
6. Deactivate virtual environment `deactivate`
7. Clean virtual environment `make clean`

#### With docker
1. You need to have docker and docker-compose installed on your system and docker process should be running
2. Run `docker-compose up`, it will create containers using postgress credentials from .env file
3. It will run, get products and store in the table `food_data` in `coding_challenge` db.
4. To verify 
    - run `docker ps` and note container_id
    - run docker exec -it {container_id} bash
    - psql postgres://aneela:aneela123@localhost:5432/coding_challenge (change user/password if you modify .env file)
    - \d will display tables inside db
    - run queries like `select count(*) from food_data;`
5. shutdown containers `docker-compose down`


#### CI/CD
GitHub action file is also written, once we commit and create a PR to main branch, the pipeline will check linting and run all tests. It fails if any test case fails

#### CASE STUDY - Theoretical Questions 
### Question 1.3
**• You want to transform ingredients into a table like structure. Which challenges could arise?**
**Answer:**
1. **Many-to-Many relationship**: ingredients are list of objects. When we transform it into table it will be a many-to-many relationship with food-data table.
As one product can have n number of ingredients and one ingredient can be part of many food products. So CRUD operations will be slow/expensive because we would have to deal with 3 tables i.e., products, ingredients and products-ingredients table.
Similarly, selection queries will also be slow because we would have to join three tables. 

2. **Language and Translation**: Ingredients are listed in different languages, so it makes data inconsistent. We would have to parse/translate the data into meaningful information. 
3. **Missing Information/Data Quality**: There is alot of missing information like <br>`"origins"`, <br>`"from_palm_oil"`, <br>`"has_sub_ingredients"` <br> It exists in some products but is missing in most products, which leads to incorrect and missing information.
A lot of preprocessing would be needed. Like `What would be the default value? How to replace missing values` etc. 

4. Ingredients further have alot of related information like which is also inconsistent (i.e., language, css code etc.) that can make the overall schema more complex. As below
   <br>`"ingredients_analysis"`
   <br>`"ingredients_with_specified_percent_n"`
   <br>`"ingredients_with_specified_percent_sum"`

So in general this type of data is a good candidate for nosql databases like **MongoDB**, **DynamoDB** etc.

### Question 1.4
**• In this case we used an API with no restriction to access it. Later in a production environment we may have to use credentials to access other API’s. Where would you store such credentials?**
<br>**Answer:**
There are different ways to save sensitive information like credentials. 
- **environment variables**: Simplest but not much secure 
- **AWS Secret Manager/SSM**: Much secure and useful if you have your infrastructure in AWS. Supports Auto rotation as well.
- **[Vault](https://www.vaultproject.io/)** : If you don't have infrastructure in cloud then it can also be an alternative (However I never used it).

### Question 2 - Outputs
### a  
[create_categories_count_df](food_data_processor/transformations/data_transformations.py)

![](screenshots/transformation-1.png)
### b 
**Assumptions**
[create_categories_min_max_df](food_data_processor/transformations/data_transformations.py)
- I calculated min and max nutri_score and get all the categories associated with min and max nutriscore. 

![](screenshots/transformation-2.png)
### c
[find_min_max_generic_name](food_data_processor/transformations/data_transformations.py)

![](screenshots/transformation-3.png)
### d
[replace_missing_values](food_data_processor/transformations/data_transformations.py)
- I replaced with most frequently occurring origins value i.e., Mode  

![](screenshots/transformation-4.png)
