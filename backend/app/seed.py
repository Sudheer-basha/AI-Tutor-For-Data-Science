import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app import models

# Fixed UUIDs for reproducibility and linking relationships
COURSE_ID = uuid.UUID("a1111111-1111-1111-1111-111111111111")

LESSON_IDS = [
    uuid.UUID(f"b2222222-2222-2222-2222-2222222222{i:02d}")
    for i in range(1, 13)
]

BADGE_IDS = [
    uuid.UUID("c3333333-3333-3333-3333-333333333301"), # Python Beginner
    uuid.UUID("c3333333-3333-3333-3333-333333333302"), # Data Cleaning
    uuid.UUID("c3333333-3333-3333-3333-333333333303"), # Visualization Master
    uuid.UUID("c3333333-3333-3333-3333-333333333304"), # ML Explorer
    uuid.UUID("c3333333-3333-3333-3333-333333333305"), # Data Science Expert
]

async def seed_data(db: AsyncSession):
    # 1. Check if course already exists
    course_query = select(models.Course).where(models.Course.course_id == COURSE_ID)
    course_result = await db.execute(course_query)
    existing_course = course_result.scalars().first()
    
    if existing_course:
        print("Database already seeded.")
        return

    print("Seeding database with Data Science syllabus...")

    # 2. Add Course
    course = models.Course(
        course_id=COURSE_ID,
        title="Personalized 3-Month Data Science Learning Path",
        description="Master Python, Statistics, Machine Learning, and Deep Learning with a guided, personalized AI-powered tutor."
    )
    db.add(course)

    # 3. Add Badges
    badges = [
        models.Badge(
            badge_id=BADGE_IDS[0],
            name="Python Beginner",
            description="Awarded for completing Week 1: Python Fundamentals.",
            milestone_type="lesson_count",
            milestone_value=1,
            icon_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="badge-icon"><path d="M12 2L2 7l10 5 10-5-10-5z"></path><path d="M2 17l10 5 10-5"></path><path d="M2 12l10 5 10-5"></path></svg>"""
        ),
        models.Badge(
            badge_id=BADGE_IDS[1],
            name="Data Cleaning Specialist",
            description="Awarded for completing Week 3: Data Cleaning & Wrangling.",
            milestone_type="lesson_count",
            milestone_value=3,
            icon_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="badge-icon"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>"""
        ),
        models.Badge(
            badge_id=BADGE_IDS[2],
            name="Visualization Master",
            description="Awarded for completing Week 4: Matplotlib & Seaborn.",
            milestone_type="lesson_count",
            milestone_value=4,
            icon_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="badge-icon"><path d="M18 20V10"></path><path d="M12 20V4"></path><path d="M6 20v-6"></path></svg>"""
        ),
        models.Badge(
            badge_id=BADGE_IDS[3],
            name="Machine Learning Explorer",
            description="Awarded for completing Month 2 (Week 8): Supervised Classification.",
            milestone_type="lesson_count",
            milestone_value=8,
            icon_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="badge-icon"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>"""
        ),
        models.Badge(
            badge_id=BADGE_IDS[4],
            name="Data Science Expert",
            description="Awarded for completing the entire 12-week course and Capstone Project.",
            milestone_type="lesson_count",
            milestone_value=12,
            icon_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="badge-icon"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>"""
        ),
    ]
    for badge in badges:
        db.add(badge)

    # 4. Syllabus details with video links
    syllabus = [
        # --- Month 1: Python Fundamentals ---
        {
            "week": 1, "month": 1,
            "title": "Introduction to Python: Variables, Loops & Functions",
            "content": """<div class="video-container">
  <iframe src="https://www.youtube.com/embed/rfscVS0vtbw" allowfullscreen></iframe>
</div>

# Week 1: Python Fundamentals for Data Science

Welcome to your first week! Watch the video above to learn Python fundamentals. Below are critical review sheets on topics and subtopics covered:

### Why Python for Data Science?
Python is the most popular language in Data Science because it is easy to read, has a rich ecosystem of libraries (NumPy, Pandas, Scikit-Learn), and possesses a massive community.

### 1. Variables and Data Types
In Python, variables are dynamically typed. You don't need to declare their type beforehand:
```python
# Integer
age = 25
# Float (decimal)
pi = 3.14159
# String (text)
name = "Alice"
# Boolean (true/false)
is_student = True
```

### 2. Control Flow: Loops and Conditionals
Loops allow you to iterate over sequences (like lists) or execute code repeatedly.
```python
# If-Else Conditional
if age >= 18:
    print("Adult")
else:
    print("Minor")

# For loop iterating through a list
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(f"I love {fruit}s!")

# While loop
count = 0
while count < 3:
    print(f"Count: {count}")
    count += 1
```

### 3. Writing Custom Functions
Functions are blocks of reusable code. Use the `def` keyword:
```python
def calculate_area(width, height):
    \"\"\"Calculates the area of a rectangle.\"\"\"
    return width * height

# Calling the function
area = calculate_area(5, 10)
print(f"Area: {area}")  # Output: 50
```

### 4. Basic Data Structures: Lists & Dictionaries
- **List**: An ordered, mutable collection. `my_list = [1, 2, 3]`
- **Dictionary**: A key-value mapping. `my_dict = {"name": "Alice", "age": 25}`
""",
            "assignment": {
                "title": "Week 1 Programming Assignment: Core Python Exercises",
                "description": """### Tasks:
Write a python function `analyze_numbers(num_list)` that takes a list of numbers and returns a dictionary containing:
1. The sum of all even numbers.
2. The count of odd numbers.
3. A list of all numbers squared.

### Starter Code:
```python
def analyze_numbers(num_list):
    # Write your logic here
    pass
```
Submit your completed Python code in the text box below. The AI tutor will grade your implementation.""",
            },
            "quizzes": [
                {
                    "question": "Which of the following is the correct syntax to define a function in Python?",
                    "options": ["function myFunc():", "def myFunc():", "create myFunc():", "method myFunc():"],
                    "correct": "B"
                },
                {
                    "question": "What is the output of print(type([1, 2, 3])) in Python?",
                    "options": ["<class 'tuple'>", "<class 'dict'>", "<class 'list'>", "<class 'array'>"],
                    "correct": "C"
                },
                {
                    "question": "How do you add an element 'orange' to an existing list named fruits?",
                    "options": ["fruits.add('orange')", "fruits.append('orange')", "fruits.insertLast('orange')", "fruits + 'orange'"],
                    "correct": "B"
                }
            ]
        },
        {
            "week": 2, "month": 1,
            "title": "Numerical Python & Pandas for Data Manipulation",
            "content": """<div class="video-container">
  <iframe src="https://www.youtube.com/embed/vmEHCJofHsg" allowfullscreen></iframe>
</div>

# Week 2: NumPy & Pandas Fundamentals

Watch the lecture on Pandas and NumPy above. Here are the core topics and syntax notes:

### 1. NumPy: Numerical Python
NumPy provides the `ndarray` object, an efficient multidimensional array.
```python
import numpy as np

# Create a 1D array
arr = np.array([1, 2, 3, 4, 5])
print(arr * 2)  # Vectorized operation: [2, 4, 6, 8, 10]

# Create a 2D matrix
matrix = np.array([[1, 2], [3, 4]])
print(matrix.shape)  # (2, 2)
```

### 2. Pandas: Panel Data
Pandas is built on top of NumPy and provides the **Series** (1D) and **DataFrame** (2D tabular) data structures.
```python
import pandas as pd

# Creating a DataFrame
data = {
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "Salary": [50000, 60000, 70000]
}
df = pd.DataFrame(data)

# Viewing data
print(df.head(2))

# Filtering Data
rich_employees = df[df["Salary"] > 55000]
print(rich_employees)
```

### 3. Essential Pandas Operations
- `df.describe()`: Prints summary statistics.
- `df.groupby("Category")["Value"].mean()`: Groups data and aggregates.
- `df.loc[row_indexer, col_indexer]`: Filters rows and columns by label.
""",
            "assignment": {
                "title": "Week 2 Assignment: Summary Statistics with Pandas",
                "description": """### Tasks:
Write a Python script that uses Pandas to:
1. Create a DataFrame containing 5 employees, their Department ('HR', 'IT', 'Finance'), and their Years of Experience.
2. Group the DataFrame by 'Department' and calculate the average 'Years of Experience' for each department.
3. Filter the employees to only show those with more than 3 years of experience.

### Starter Code:
```python
import pandas as pd

# 1. Create DataFrame
# ...
```""",
            },
            "quizzes": [
                {
                    "question": "Which object is the primary 2D data structure in Pandas, representing tabular data?",
                    "options": ["Series", "NDArray", "DataFrame", "Panel"],
                    "correct": "C"
                },
                {
                    "question": "In NumPy, how do you find the shape (dimensions) of an array named 'arr'?",
                    "options": ["arr.shape()", "arr.shape", "arr.get_shape", "arr.dimension"],
                    "correct": "B"
                }
            ]
        },
        {
            "week": 3, "month": 1,
            "title": "Data Cleaning, Handling Missing Values & Wrangling",
            "content": """<div class="video-container">
  <iframe src="https://www.youtube.com/embed/bDhvCo30gwc" allowfullscreen></iframe>
</div>

# Week 3: Data Cleaning & Wrangling

Watch the walkthrough on data cleaning above. Make sure to study the following notes:

### 1. Handling Missing Data
Missing data is usually represented as `NaN` (Not a Number) in Pandas.
- **Detecting missing values**: `df.isnull().sum()`
- **Dropping missing values**: `df.dropna()`
- **Imputing (filling) missing values**: `df.fillna(value)`

```python
# Filling missing ages with the column mean
mean_age = df["Age"].mean()
df["Age"] = df["Age"].fillna(mean_age)
```

### 2. Dropping Duplicates
Duplicate rows can bias our analysis:
```python
# Drop exact duplicates
df = df.drop_duplicates()
```

### 3. String & Categorical Transformations
Cleaning string inputs and converting text categories into clean variables:
```python
# Strip spaces and convert to lowercase
df["Email"] = df["Email"].str.strip().str.lower()

# Renaming Columns
df = df.rename(columns={"OldName": "new_name"})
```
""",
            "assignment": {
                "title": "Week 3 Assignment: Cleaning a Raw Customer Dataset",
                "description": """### Tasks:
You are given a dirty DataFrame. Write a function `clean_dataset(df)` to:
1. Fill missing values in the 'Age' column with the median age.
2. Remove duplicate rows.
3. Convert the 'PurchaseAmount' column to float (it currently contains '$' signs, e.g., '$100.50').

### Starter Code:
```python
import pandas as pd

def clean_dataset(df):
    # Write cleaning operations here
    return df
```""",
            },
            "quizzes": [
                {
                    "question": "Which Pandas function is used to replace null (NaN) values with a default value?",
                    "options": ["df.dropna()", "df.replace_null()", "df.fillna()", "df.clean()"],
                    "correct": "C"
                },
                {
                    "question": "How do you detect the total number of missing values in each column of a DataFrame?",
                    "options": ["df.isna().sum()", "df.check_nulls()", "df.isnull().count()", "df.describe()"],
                    "correct": "A"
                }
            ]
        },
        {
            "week": 4, "month": 1,
            "title": "Data Visualization with Matplotlib & Seaborn",
            "content": """<div class="video-container">
  <iframe src="https://www.youtube.com/embed/O5xeyoRL95U" allowfullscreen></iframe>
</div>

# Week 4: Data Visualization

Watch the tutorial above for plotting with Matplotlib and Seaborn. Review topics and commands:

### 1. Matplotlib
Matplotlib is the core plotting library in Python, offering low-level control.
```python
import matplotlib.pyplot as plt

x = [1, 2, 3, 4]
y = [10, 20, 25, 30]

plt.plot(x, y, label="Trend", color="blue", marker="o")
plt.title("Simple Line Plot")
plt.xlabel("X Axis")
plt.ylabel("Y Axis")
plt.legend()
plt.show()
```

### 2. Seaborn
Seaborn is built on top of Matplotlib and integrates directly with Pandas DataFrames to produce beautiful statistical graphics with minimal code.
```python
import seaborn as sns
import pandas as pd

# Load sample dataset
tips = sns.load_dataset("tips")

# Create a scatter plot with hue mapping
sns.scatterplot(data=tips, x="total_bill", y="tip", hue="smoker")
plt.title("Total Bill vs Tip")
plt.show()
```

### 3. Common Plots
- **Histogram**: Displays distributions (`sns.histplot`).
- **Box Plot**: Shows outliers and quartiles (`sns.boxplot`).
- **Heatmap**: Visualizes correlation matrices (`sns.heatmap`).
""",
            "assignment": {
                "title": "Week 4 Assignment: Create Visual Analytics Report",
                "description": """### Tasks:
Write the code to plot:
1. A Seaborn boxplot showing the distribution of 'sales' across different 'stores' (use categorical store names).
2. Add a title, label the axes, and set the style to 'darkgrid' using Seaborn.
(Since this is visual, submit the plotting script. The AI tutor will review the plotting commands and logic).""",
            },
            "quizzes": [
                {
                    "question": "Which Seaborn function is best suited to display a correlation matrix visually?",
                    "options": ["sns.barplot", "sns.heatmap", "sns.pairplot", "sns.boxplot"],
                    "correct": "B"
                },
                {
                    "question": "How do you display a legend on a Matplotlib plot?",
                    "options": ["plt.show_legend()", "plt.legend()", "plt.add_labels()", "plt.legend=True"],
                    "correct": "B"
                }
            ]
        },
        # --- Month 2: Statistics & ML ---
        {
            "week": 5, "month": 2,
            "title": "Introduction to Statistical Data Analysis",
            "content": """<div class="video-container">
  <iframe src="https://www.youtube.com/embed/xxpc-HPKN28" allowfullscreen></iframe>
</div>

# Week 5: Statistics Basics

Watch the Statistics lectures above. Review these fundamental mathematical definitions:

### 1. Measures of Central Tendency
- **Mean**: The mathematical average.
- **Median**: The middle value when sorted. Robust to outliers.
- **Mode**: The most frequent value.

### 2. Measures of Dispersion (Spread)
- **Variance**: Average squared deviation from the mean.
- **Standard Deviation (SD)**: Square root of variance. Tells us how spread out the numbers are.
- **Percentiles**: Indicates the value below which a given percentage of observations fall (e.g. 75th percentile).

### 3. Normal Distribution
A bell-shaped curve where 68% of data falls within 1 standard deviation, and 95% falls within 2 standard deviations of the mean.
""",
            "assignment": {
                "title": "Week 5 Assignment: Statistical Computations",
                "description": """### Tasks:
Write a Python script (using NumPy/Pandas) to:
1. Load a list of scores: `[90, 85, 12, 95, 88, 92, 100, 89]`.
2. Compute the Mean, Median, and Standard Deviation.
3. Identify if there is an outlier in the scores, and write a brief description of how it affects the Mean vs Median.
Submit your script and written analysis.""",
            },
            "quizzes": [
                {
                    "question": "Which measure of central tendency is least affected by extreme outliers in a dataset?",
                    "options": ["Mean", "Median", "Mode", "Standard Deviation"],
                    "correct": "B"
                },
                {
                    "question": "What percentage of data falls within two standard deviations of the mean in a Normal Distribution?",
                    "options": ["68%", "95%", "99.7%", "50%"],
                    "correct": "B"
                }
            ]
        },
        {
            "week": 6, "month": 2,
            "title": "Probability Distributions & Hypothesis Testing",
            "content": """<div class="video-container">
  <iframe src="https://www.youtube.com/embed/tTeMYuS87oU" allowfullscreen></iframe>
</div>

# Week 6: Probability & Hypothesis Testing

Watch the lecture on Hypothesis testing above. Study the core testing concepts:

### 1. Key Concepts
- **Null Hypothesis (H0)**: Assumption that there is no effect or difference.
- **Alternative Hypothesis (Ha)**: What we want to prove (e.g. active group performs better).
- **p-value**: The probability of observing our results if H0 is true. If p-value < 0.05, we reject the null hypothesis.

### 2. Types of Tests
- **t-test**: Compares the means of two groups.
- **ANOVA**: Compares the means of three or more groups.
- **Chi-Square Test**: Compares categorical frequencies.
""",
            "assignment": {
                "title": "Week 6 Assignment: T-test Implementation",
                "description": """### Tasks:
You want to test if a website design update increased sales. Group A (old design) sales: `[12, 15, 18, 14, 15]`. Group B (new design) sales: `[19, 22, 24, 20, 21]`.
Write a script using `scipy.stats` to:
1. Conduct an independent 2-sample t-test.
2. Print the p-value.
3. Conclude if the new design is significantly better (using alpha=0.05).""",
            },
            "quizzes": [
                {
                    "question": "If your hypothesis test yields a p-value of 0.012, and alpha is 0.05, what is the conclusion?",
                    "options": ["Reject the Null Hypothesis", "Fail to Reject the Null Hypothesis", "Accept the Null Hypothesis", "Test is inconclusive"],
                    "correct": "A"
                },
                {
                    "question": "Which statistical test compares categorical distributions?",
                    "options": ["T-test", "ANOVA", "Chi-Square Test", "Z-test"],
                    "correct": "C"
                }
            ]
        },
        {
            "week": 7, "month": 2,
            "title": "Linear Regression and Model Evaluation",
            "content": """<div class="video-container">
  <iframe src="https://www.youtube.com/embed/E5Rjxo4sYLt" allowfullscreen></iframe>
</div>

# Week 7: Linear Regression

Watch the video tutorial on linear regression above. Study these notes:

### 1. Mathematical Equation
$$y = \\beta_0 + \\beta_1 x + \\epsilon$$
Where:
- $y$ is the dependent variable (target).
- $x$ is the independent variable (feature).
- $\\beta_0$ is the intercept.
- $\\beta_1$ is the slope coefficient.

### 2. Training with Scikit-Learn
```python
from sklearn.linear_model import LinearRegression
import numpy as np

# Prepare data
X = np.array([[1], [2], [3], [4]])
y = np.array([2, 4, 6, 8])

# Train model
model = LinearRegression()
model.fit(X, y)

# Predict
print(model.predict([[5]]))  # Output: [10]
```

### 3. Evaluation Metrics
- **Mean Absolute Error (MAE)**: Average absolute difference.
- **Mean Squared Error (MSE)**: Penalizes larger errors.
- **R-squared ($R^2$)**: Variance explained by the model (0 to 1).
""",
            "assignment": {
                "title": "Week 7 Assignment: Linear Regression on Housing Prices",
                "description": """### Tasks:
Use scikit-learn's `LinearRegression` to:
1. Train a model predicting House Price ($Y$) based on Square Footage ($X$). Data: $X = [1000, 1500, 1800, 2400]$, $Y = [200000, 290000, 340000, 460000]$.
2. Make a price prediction for a 2000 sq ft house.
3. Print the slope coefficient and intercept. Explain what the coefficient means in real-world terms.""",
            },
            "quizzes": [
                {
                    "question": "What does a R-squared score of 0.85 indicate about a regression model?",
                    "options": ["The model is 85% accurate", "85% of target variance is explained by features", "The error is 15%", "The slope coefficient is 0.85"],
                    "correct": "B"
                },
                {
                    "question": "Which of the following is the standard loss function optimized by Linear Regression?",
                    "options": ["Mean Absolute Error", "Mean Squared Error / Sum of Squared Residuals", "Cross Entropy", "Binary Loss"],
                    "correct": "B"
                }
            ]
        },
        {
            "week": 8, "month": 2,
            "title": "Supervised Machine Learning: Classification Algorithms",
            "content": """<div class="video-container">
  <iframe src="https://www.youtube.com/embed/I3G0Y5Gsxyg" allowfullscreen></iframe>
</div>

# Week 8: Classification Algorithms

Watch the video lecture on Machine Learning classification above. Review these notes:

### 1. Algorithms
- **Logistic Regression**: Outputs a probability mapped to a sigmoid function.
- **Decision Trees**: Splits data based on feature thresholds.
- **Random Forest**: An ensemble of decision trees.

### 2. Evaluation Metrics
- **Confusion Matrix**: Table of TP, FP, TN, FN.
- **Accuracy**: Correct predictions / Total predictions.
- **Precision**: TP / (TP + FP). Important when false positives are costly.
- **Recall (Sensitivity)**: TP / (TP + FN). Important when false negatives are costly.
- **F1-Score**: Harmonic mean of Precision and Recall.
""",
            "assignment": {
                "title": "Week 8 Assignment: Logistic Regression Classifier",
                "description": """### Tasks:
Create a machine learning pipeline using `scikit-learn`:
1. Use `sklearn.datasets.make_classification` to generate a synthetic dataset of 200 items.
2. Split it into training (80%) and testing (20%) datasets.
3. Train a `LogisticRegression` classifier, make predictions, and print the resulting `classification_report`.
Submit the code and explain the difference between Precision and Recall.""",
            },
            "quizzes": [
                {
                    "question": "Which metric is most crucial to evaluate a medical model predicting a rare disease where missing a diagnosis (false negative) is catastrophic?",
                    "options": ["Precision", "Recall / Sensitivity", "Accuracy", "Specificity"],
                    "correct": "B"
                },
                {
                    "question": "What is the output activation function used in binary Logistic Regression to bound probabilities between 0 and 1?",
                    "options": ["ReLU", "Tanh", "Sigmoid", "Softmax"],
                    "correct": "C"
                }
            ]
        },
        # --- Month 3: Deep Learning & Projects ---
        {
            "week": 9, "month": 3,
            "title": "Deep Learning: Fundamentals of Neural Networks",
            "content": """<div class="video-container">
  <iframe src="https://www.youtube.com/embed/aircAruvnKk" allowfullscreen></iframe>
</div>

# Week 9: Introduction to Neural Networks

Watch the visual neural networks lecture above. Here are the core topics covered:

### 1. The Artificial Neuron (Perceptron)
An input vector is multiplied by weights, summed with a bias, and passed through an activation function:
$$z = \\sum (w_i x_i) + b$$
$$a = g(z)$$

### 2. Activation Functions
- **Sigmoid**: Compresses output to (0, 1).
- **ReLU (Rectified Linear Unit)**: $f(x) = \\max(0, x)$. Standard for hidden layers.
- **Softmax**: Multi-class probability distributions.

### 3. Backpropagation and Optimization
- **Loss Function**: Measures prediction error.
- **Gradient Descent**: Calculates derivatives of the loss with respect to weights, adjusting them to minimize error.
""",
            "assignment": {
                "title": "Week 9 Assignment: Neural Network Conceptualization",
                "description": """### Tasks:
Answer the following questions in a detailed written explanation:
1. What is the role of activation functions in hidden layers? Why is ReLU generally preferred over Sigmoid in deep hidden layers?
2. Briefly describe the difference between forward propagation and backpropagation.""",
            },
            "quizzes": [
                {
                    "question": "Which issue is a major reason Sigmoid activation functions are avoided in deep hidden layers?",
                    "options": ["Vanishing Gradient Problem", "Overfitting", "Slow execution", "Non-differentiability"],
                    "correct": "A"
                },
                {
                    "question": "What is the primary function of backpropagation in training neural networks?",
                    "options": ["Loading the input data", "Updating network weights based on the loss gradient", "Adding new neurons to layers", "Applying the activation function"],
                    "correct": "B"
                }
            ]
        },
        {
            "week": 10, "month": 3,
            "title": "Building Deep Learning Models with TensorFlow/Keras",
            "content": """<div class="video-container">
  <iframe src="https://www.youtube.com/embed/tpCFfeUEGs8" allowfullscreen></iframe>
</div>

# Week 10: Deep Learning with TensorFlow & Keras

Watch the TensorFlow course above. Review Keras model configuration syntax:

### 1. Designing a Sequential Model
```python
import tensorflow as tf
from tensorflow.keras import layers, models

# Define a standard feedforward model
model = models.Sequential([
    layers.Dense(64, activation='relu', input_shape=(10,)),
    layers.Dense(32, activation='relu'),
    layers.Dense(1, activation='sigmoid') # Binary classifier
])
```

### 2. Compilation and Training
Specify the optimizer, loss function, and metrics:
```python
model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# Training the model
# model.fit(X_train, y_train, epochs=10, batch_size=32)
```
""",
            "assignment": {
                "title": "Week 10 Assignment: Construct Keras Model",
                "description": """### Tasks:
Write a Python script using TensorFlow/Keras to:
1. Define a `Sequential` model to classify a 28x28 grayscale image (784 flat features) into 10 target classes (e.g. MNIST digits).
2. Use one Flatten input layer, one hidden Dense layer with 128 units and ReLU activation, and a final Dense output layer with Softmax.
3. Compile the model with the 'adam' optimizer, 'sparse_categorical_crossentropy' loss, and 'accuracy' metric.""",
            },
            "quizzes": [
                {
                    "question": "Which loss function is appropriate for a multi-class classification problem where label integers (0, 1, 2...) are provided?",
                    "options": ["categorical_crossentropy", "sparse_categorical_crossentropy", "binary_crossentropy", "mean_squared_error"],
                    "correct": "B"
                },
                {
                    "question": "In a Keras layer: layers.Dense(64), what does the number 64 represent?",
                    "options": ["The batch size", "The number of epochs", "The number of neurons in the layer", "The learning rate"],
                    "correct": "C"
                }
            ]
        },
        {
            "week": 11, "month": 3,
            "title": "Model Deployment & API Development",
            "content": """<div class="video-container">
  <iframe src="https://www.youtube.com/embed/h5wLuVZr0yg" allowfullscreen></iframe>
</div>

# Week 11: Model Deployment

Watch the FastAPI model deployment tutorial above. Learn the serialization syntax:

### 1. Serializing Models (Pickle)
First, save the trained model to disk:
```python
import pickle

# Save model
with open('model.pkl', 'wb') as f:
    pickle.dump(trained_model, f)

# Load model
# with open('model.pkl', 'rb') as f:
#     model = pickle.load(f)
```

### 2. Creating APIs with FastAPI
```python
from fastapi import FastAPI
import pickle
import numpy as np

app = FastAPI()
model = pickle.load(open('model.pkl', 'rb'))

@app.post("/predict")
def predict(features: list):
    data = np.array([features])
    prediction = model.predict(data)
    return {"prediction": int(prediction[0])}
```
""",
            "assignment": {
                "title": "Week 11 Assignment: Create ML Prediction API",
                "description": """### Tasks:
Write the complete code for a FastAPI application that:
1. Loads a saved model file named `classifier.pkl` on startup.
2. Exposes a POST endpoint `/predict` accepting a JSON payload with key `features` (a list of floats).
3. Evaluates predictions and returns `{"class": predicted_value}`.""",
            },
            "quizzes": [
                {
                    "question": "Which Python library is standard for serializing (saving to file) machine learning models?",
                    "options": ["json", "csv", "pickle / joblib", "numpy"],
                    "correct": "C"
                },
                {
                    "question": "What is the main advantage of using FastAPI to serve models?",
                    "options": ["Fast execution speeds and automatic OpenAPI documentation generation", "It trains neural networks faster", "It replaces the need for scikit-learn", "It manages GPU memory automatically"],
                    "correct": "A"
                }
            ]
        },
        {
            "week": 12, "month": 3,
            "title": "Capstone Project: End-to-End Data Science System",
            "content": """<div class="video-container">
  <iframe src="https://www.youtube.com/embed/GLSj2fPpxP8" allowfullscreen></iframe>
</div>

# Week 12: Capstone Project

Watch the end-to-end Data Science capstone project guide above. Review the checklist of tasks:

### The Capstone Project
You will build an end-to-end data pipeline from scratch:
1. **Data Ingestion**: Load a real-world CSV dataset.
2. **Exploratory Data Analysis (EDA)**: Calculate stats and create visualizations.
3. **Data Cleaning**: Handle outliers and missing data.
4. **Machine Learning**: Train and optimize a classifier or regressor.
5. **Evaluation**: Generate performance metrics and discuss business value.
""",
            "assignment": {
                "title": "Week 12 Assignment: Final Capstone Submission",
                "description": """### Tasks:
Submit a summary outline or python script detailing your Capstone project workflow:
1. Identify the dataset you are using.
2. Outline your cleaning, preprocessing, and model training decisions.
3. State the final model performance metric (e.g. Accuracy or R2 score).
(Submit the detailed workflow script or markdown report. The AI tutor will grade it for completeness).""",
            },
            "quizzes": [
                {
                    "question": "Which of the following describes the correct order of a standard Data Science workflow?",
                    "options": [
                        "Train Model -> Deploy -> Load Data -> Clean Data",
                        "Load Data -> Clean Data -> Train Model -> Evaluate -> Deploy",
                        "Clean Data -> Deploy -> Load Data -> Evaluate",
                        "Deploy -> Evaluate -> Train Model -> Load Data"
                    ],
                    "correct": "B"
                }
            ]
        }
    ]

    for index, item in enumerate(syllabus):
        # Create Lesson
        lesson = models.Lesson(
            lesson_id=LESSON_IDS[index],
            course_id=COURSE_ID,
            title=item["title"],
            content=item["content"],
            week_number=item["week"],
            month_number=item["month"],
            order_index=index + 1
        )
        db.add(lesson)

        # Create Assignment
        assignment = models.Assignment(
            assignment_id=uuid.uuid4(),
            lesson_id=LESSON_IDS[index],
            title=item["assignment"]["title"],
            description=item["assignment"]["description"],
            type="coding"
        )
        db.add(assignment)

        # Create Quizzes
        for q_item in item["quizzes"]:
            quiz = models.Quiz(
                quiz_id=uuid.uuid4(),
                lesson_id=LESSON_IDS[index],
                question=q_item["question"],
                options=q_item["options"],
                correct_option=q_item["correct"]
            )
            db.add(quiz)

    await db.commit()
    print("Database seeding completed successfully.")
