import matplotlib.pyplot as plt

import src as dp
# dp.Graph.from_csv("graphs/production_right.csv").draw()
dp.Graph.from_obj("graphs/graph.obj").draw()
plt.show()
# #%%
# G = dp.Graph.from_csv("graphs/initial2_graph.csv")
# L = dp.Graph.from_csv("graphs/production_left.csv")
# R = dp.Graph.from_csv("graphs/production_right.csv")
# #%%
# G.draw()
# #%%
# def load_mappings(filename):
#     with open(filename, 'r') as f:
#         mapping_line = f.readline().strip()
#         return [int(x.strip()) for x in mapping_line.split(',') if x.strip()]
# #%%
# mapping = load_mappings("graphs/mapping.csv")
# #%%
# production = dp.Production(L, R)
# result_graph = production.apply(G, mapping)
# #%%
# production.draw()
# #%%
# result_graph.draw()