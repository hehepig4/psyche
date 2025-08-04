
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties ,fontManager
import seaborn as sns
import numpy as np
import pandas as pd


font_path = './classify/fonts/times.ttf'
fontManager.addfont(path=font_path)
prop = FontProperties(fname=font_path)

sns.set(context='paper', 
        style='ticks', 
        palette='deep', 
        font=prop.get_name(),
        font_scale=2.8, 
        rc={
            'mathtext.fontset': 'stix',
            'pdf.fonttype': 42,
            'lines.linewidth' : 4,
            'lines.markersize' : 8,
            'font.weight': 'bold',
            'axes.labelweight': 'bold',
            'axes.titleweight': 'bold',
            'figure.titleweight': 'bold'
        }
)
sns.despine()
categories = [
    "No Check",
    "C$\\rightarrow$C",
    "C$\\rightarrow$I",
    "I$\\rightarrow$I",
    "I$\\rightarrow$C",

]
r1_counts  = [125, 771, 0, 35, 5]
qwq_counts = [69,  826, 3, 39, 0]


r1_total = sum(r1_counts)
qwq_total = sum(qwq_counts)
r1_percentages = [count/r1_total*100 for count in r1_counts]
qwq_percentages = [count/qwq_total*100 for count in qwq_counts]


dataset_source = [["Category", "R1", "QwQ"]]
for cat, r1, qwq in zip(categories, r1_counts, qwq_counts):
    dataset_source.append([cat, r1, qwq])


r1_data = [(cat, count, f"{count} ({percentage:.1f}%)") 
           for cat, count, percentage in zip(categories, r1_counts, r1_percentages)]
qwq_data = [(cat, count, f"{count} ({percentage:.1f}%)") 
            for cat, count, percentage in zip(categories, qwq_counts, qwq_percentages)]


fig, ax = plt.subplots(1, 1, figsize=(12, 8))


filtered_categories = categories
filtered_r1_counts = r1_counts
filtered_qwq_counts = qwq_counts


colors = ['#95A5A6', '#27AE60', '#E74C3C', '#3498DB', '#9B59B6']


y_pos = np.arange(2)
bar_height = 0.5 
y_spacing = 0.6 
text_pos = ['center', 'center', 'top','center','top']

cumulative_r1 = 0
for i, (cat, count) in enumerate(zip(filtered_categories, filtered_r1_counts)):
    if count > 0: 
        ax.barh(y_pos[0] * y_spacing, count, left=cumulative_r1, color=colors[i], 
                label=cat if i == 0 else "", alpha=0.8, height=bar_height)
        
        
        if count <= 10: 
            
            bar_center_x = cumulative_r1 + count/2
            text_x = 800 
            text_y = y_pos[0] * y_spacing - bar_height/2 + 0.4
            
            
            ax.annotate(str(count), 
                       xy=(bar_center_x, y_pos[0] * y_spacing), 
                       xytext=(text_x, text_y),
                       ha='center', va='bottom', 
                       fontweight='bold', fontsize=24,
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8, edgecolor='black'),
                       arrowprops=dict(arrowstyle='-', 
                                     connectionstyle="angle3,angleA=0,angleB=90",
                                     color='black', lw=1.5))
        else:
           
            ax.text(cumulative_r1 + count/2, y_pos[0] * y_spacing, str(count), 
                   ha='center', va=text_pos[i], fontweight='bold', fontsize=24)
        cumulative_r1 += count


cumulative_qwq = 0
for i, (cat, count) in enumerate(zip(filtered_categories, filtered_qwq_counts)):
    if count > 0: 
        ax.barh(y_pos[1] * y_spacing, count, left=cumulative_qwq, color=colors[i], 
                alpha=0.8, height=bar_height)
        
       
        if count <= 10:  
            bar_center_x = cumulative_qwq + count/2
            text_x = 800 
            text_y = y_pos[1] * y_spacing + bar_height/2 - 0.4
            
            
            ax.annotate(str(count), 
                       xy=(bar_center_x, y_pos[1] * y_spacing), 
                       xytext=(text_x, text_y),
                       ha='center', va='top', 
                       fontweight='bold', fontsize=24,
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8, edgecolor='black'),
                       arrowprops=dict(arrowstyle='-', 
                                     connectionstyle="angle3,angleA=0,angleB=-90",
                                     color='black', lw=1.5))
        else:
            ax.text(cumulative_qwq + count/2, y_pos[1] * y_spacing, str(count), 
                   ha='center', va=text_pos[i], fontweight='bold', fontsize=24)
        cumulative_qwq += count

#ax.set_xlabel('Count', fontweight='bold', fontsize=18)
ax.set_yticks(y_pos * y_spacing)
ax.set_yticklabels(['R1', 'QwQ'], rotation=90, va='center')  

max_total = max(sum(filtered_r1_counts), sum(filtered_qwq_counts))
ax.set_xlim(0, max_total)

current_xticks = list(ax.get_xticks())
if max_total not in current_xticks:
    current_xticks = current_xticks[:-1] + [max_total]
    ax.set_xticks(sorted(current_xticks))


legend_elements = []
for i, cat in enumerate(filtered_categories):
    if filtered_r1_counts[i] > 0 or filtered_qwq_counts[i] > 0:
        legend_elements.append(plt.Rectangle((0, 0), 1, 1, color=colors[i], alpha=0.8, label=cat))

ax.legend(handles=legend_elements, loc='center', bbox_to_anchor=(0.5, 1.05), 
          ncol=len(legend_elements), fontsize=20, frameon=True, )
ax.grid(axis='x', alpha=0.3)


ax.margins(y=0.05)


plt.tight_layout()


plt.savefig('./classify/figures/horizontal_stacked_bar_comparison.pdf', dpi=300, bbox_inches='tight')



