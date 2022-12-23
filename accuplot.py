import pandas as pd
from matplotlib import pyplot as plt

columns = ["Sample", "TP","GA","NA","DR"] 
df = pd.read_csv("accuracy.csv", usecols=columns,skipinitialspace = True)
df = pd.DataFrame(df)
df = df.infer_objects()
df[['GA', 'NA']] = df[['GA', 'NA']].apply(pd.to_numeric)
print(type(df["GA"][0]))
plt.plot(df["Sample"],df["NA"], df["GA"])
plt.legend(["Test", "Trained"])
plt.xlabel("Sample")
plt.ylabel("accuracy")
plt.show()