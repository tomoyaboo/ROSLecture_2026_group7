import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge

class ESN:
    def __init__(
        self,
        n_input=1,
        n_reservoir=100,
        spectral_radius=0.9,
        sparsity=0.1,
        leak_rate=1.0,
        ridge_alpha=1e-6
    ):
        self.n_input = n_input
        self.n_reservoir = n_reservoir
        self.leak_rate = leak_rate

        self.Win = np.random.uniform(-1, 1, (n_reservoir, n_input))
        W = np.random.uniform(-1, 1, (n_reservoir, n_reservoir))
        mask = np.random.rand(n_reservoir, n_reservoir) < sparsity
        W *= mask

        eigvals = np.linalg.eigvals(W)
        radius = np.max(np.abs(eigvals))
        self.W = W * (spectral_radius / radius)

        self.readout = Ridge(alpha=ridge_alpha)
        self.last_state = None

    def _update(self, x, u):
        pre = self.Win @ u + self.W @ x
        x_new = np.tanh(pre)
        return (1 - self.leak_rate) * x + self.leak_rate * x_new

    def fit(self, U_train, Y_train, washout=50):
        x = np.zeros(self.n_reservoir)
        states = []

        for t in range(len(U_train)):
            u = np.array([U_train[t]])
            x = self._update(x, u)
            if t >= washout:
                states.append(x.copy())

        self.last_state = x.copy()
        states = np.array(states)
        self.readout.fit(states, Y_train[washout:])

    def predict(self, U_test):
        if self.last_state is not None:
            x = self.last_state.copy()
        else:
            x = np.zeros(self.n_reservoir)
            
        outputs = []
        for t in range(len(U_test)):
            u = np.array([U_test[t]])
            x = self._update(x, u)
            y = self.readout.predict(x.reshape(1, -1))
            outputs.append(y[0])

        return np.array(outputs)

# =====================
# NARMA10 データ生成関数（安全装置付き）
# =====================
def generate_narma10(length=2000, discard=100):
    total_length = length + discard
    
    # 無限大に発散した場合は作り直すループ
    while True:
        u = np.random.uniform(0, 0.5, total_length)
        y = np.zeros(total_length)
        diverged = False
        
        for t in range(9, total_length - 1):
            y[t+1] = 0.3 * y[t] + 0.05 * y[t] * np.sum(y[t-9:t+1]) + 1.5 * u[t-9] * u[t] + 0.1
            
            # 安全装置：値が2.0を超えたら（発散の兆候）、やり直しフラグを立ててループを抜ける
            if y[t+1] > 2.0 or np.isnan(y[t+1]):
                diverged = True
                break
                
        # 爆発せずに無事最後まで生成できたら、ループを終了してデータを返す
        if not diverged:
            return u[discard:], y[discard:]


# =====================
# 実験の設定
# =====================
leak_rates = np.arange(0.05, 1.05, 0.05)
trials = 5
train_size = 1500

results_leak_rates = []
results_accuracies = []

print("--- NARMA10 リークレート検証を開始します ---")

for lr in leak_rates:
    trial_accuracies = []
    
    for trial in range(trials):
        u, y = generate_narma10(length=2000)
        U = u[:-1]
        Y = y[1:].reshape(-1, 1)
        
        U_train, Y_train = U[:train_size], Y[:train_size]
        U_test, Y_test = U[train_size:], Y[train_size:]
        
        esn = ESN(
            n_reservoir=100,
            spectral_radius=0.9,
            sparsity=0.1,
            leak_rate=lr
        )
        
        esn.fit(U_train, Y_train, washout=50)
        Y_pred = esn.predict(U_test)
        
        # 精度計算
        nmse = np.mean((Y_test.flatten() - Y_pred.flatten())**2) / np.var(Y_test)
        accuracy = (1.0 - nmse) * 100.0
        trial_accuracies.append(accuracy)
        
    avg_accuracy = np.mean(trial_accuracies)
    results_leak_rates.append(lr)
    results_accuracies.append(avg_accuracy)
    
    print(f"リークレート: {lr:.2f} | 平均精度: {avg_accuracy:7.2f} %")

# =====================
# グラフの描画
# =====================
plt.figure(figsize=(8, 5))
plt.plot(results_leak_rates, results_accuracies, marker='o', color='tab:orange', linestyle='-')
plt.xlabel('Leak Rate')
plt.ylabel('Accuracy (%)')
plt.title('NARMA10 Task: Leak Rate vs Accuracy (5-trial average)')
plt.grid(True)
plt.xticks(np.arange(0, 1.1, 0.1))
plt.show()