import torch
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.patches import Rectangle

from dataset import get_datasets
from model_utils import create_model

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
NUM_CLASSES = 3
class_names = ['Normal', 'Pneumonia', 'TB']

def evaluate_test(model, test_loader, save_figures=True):
    """
    Evaluate the model on test set and generate confusion matrix and classification report figures
    """
    model.eval()
    all_preds = []
    all_labels = []
    all_confidences = []

    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            outputs = model(images)
            # Apply softmax to get probabilities
            probabilities = torch.softmax(outputs, dim=1)
            # Get prediction confidence (max probability)
            confidences = torch.max(probabilities, dim=1)[0]
            preds = outputs.argmax(dim=1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_confidences.extend(confidences.cpu().numpy())

    # Generate classification report
    report = classification_report(all_labels, all_preds, target_names=class_names, output_dict=True)
    
    # Print detailed results
    print("Classification Report:")
    print(classification_report(all_labels, all_preds, target_names=class_names))
    print(f"\nOverall Accuracy: {report['accuracy']:.4f}")
    print(f"Macro Average F1-Score: {report['macro avg']['f1-score']:.4f}")
    print(f"Weighted Average F1-Score: {report['weighted avg']['f1-score']:.4f}")
    
    # Create confusion matrix
    cm = confusion_matrix(all_labels, all_preds)
    
    if save_figures:
        # Figure 1: Confusion Matrix
        create_confusion_matrix_figure(cm, class_names)
        
        # Figure 2: Classification Report Visualization
        create_classification_report_figure(report, class_names)
        
        # Additional: Confidence distribution analysis
        create_confidence_analysis(all_confidences, all_labels, all_preds, class_names)
    
    return report, cm, all_confidences

def create_confusion_matrix_figure(cm, class_names):
    """
    Create and save confusion matrix figure
    """
    plt.figure(figsize=(8, 6))
    
    # Calculate percentages
    cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100
    
    # Create heatmap with both counts and percentages
    ax = sns.heatmap(cm, annot=False, fmt='d', cmap='Blues', 
                     xticklabels=class_names, yticklabels=class_names,
                     cbar_kws={'label': 'Number of Samples'})
    
    # Add custom annotations with counts and percentages
    for i in range(len(class_names)):
        for j in range(len(class_names)):
            text = f'{cm[i,j]}\n({cm_normalized[i,j]:.1f}%)'
            ax.text(j+0.5, i+0.5, text, ha='center', va='center', 
                   fontsize=12, fontweight='bold' if i == j else 'normal')
    
    plt.xlabel('Predicted Label', fontsize=12, fontweight='bold')
    plt.ylabel('True Label', fontsize=12, fontweight='bold')
    plt.title('Confusion Matrix for Test Set Predictions', fontsize=14, fontweight='bold', pad=20)
    
    # Add grid lines for better readability
    plt.grid(False)
    
    plt.tight_layout()
    plt.savefig('figures/confusion_matrix.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Confusion matrix saved as 'figures/confusion_matrix.png'")

def create_classification_report_figure(report, class_names):
    """
    Create and save classification report visualization
    """
    # Extract metrics for each class
    metrics = ['precision', 'recall', 'f1-score']
    
    # Prepare data for plotting
    data = []
    for class_name in class_names:
        for metric in metrics:
            data.append({
                'Class': class_name,
                'Metric': metric.replace('-', '-\n').title(),
                'Value': report[class_name][metric]
            })
    
    # Add overall metrics
    overall_metrics = [
        {'Class': 'Macro Avg', 'Metric': 'Precision', 'Value': report['macro avg']['precision']},
        {'Class': 'Macro Avg', 'Metric': 'Recall', 'Value': report['macro avg']['recall']},
        {'Class': 'Macro Avg', 'Metric': 'F1-Score', 'Value': report['macro avg']['f1-score']},
        {'Class': 'Weighted Avg', 'Metric': 'Precision', 'Value': report['weighted avg']['precision']},
        {'Class': 'Weighted Avg', 'Metric': 'Recall', 'Value': report['weighted avg']['recall']},
        {'Class': 'Weighted Avg', 'Metric': 'F1-Score', 'Value': report['weighted avg']['f1-score']},
    ]
    
    df = pd.DataFrame(data)
    
    # Create the figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot 1: Individual class metrics
    pivot_df = df.pivot(index='Class', columns='Metric', values='Value')
    
    x = np.arange(len(class_names))
    width = 0.25
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Blue, Orange, Green
    
    for i, metric in enumerate(metrics):
        values = [report[class_name][metric] for class_name in class_names]
        bars = ax1.bar(x + i*width, values, width, label=metric.title(), color=colors[i], alpha=0.8)
        
        # Add value labels on bars
        for bar, val in zip(bars, values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{val:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax1.set_xlabel('Class', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax1.set_title('Classification Metrics by Class', fontsize=13, fontweight='bold')
    ax1.set_xticks(x + width)
    ax1.set_xticklabels(class_names)
    ax1.legend()
    ax1.set_ylim(0, 1.1)
    ax1.grid(axis='y', alpha=0.3)
    
    # Plot 2: Overall metrics comparison
    overall_data = {
        'Accuracy': [report['accuracy']] * 3,
        'Macro Avg': [report['macro avg'][metric] for metric in metrics],
        'Weighted Avg': [report['weighted avg'][metric] for metric in metrics]
    }
    
    x2 = np.arange(len(metrics))
    width2 = 0.25
    
    colors2 = ['#d62728', '#9467bd', '#8c564b']  # Red, Purple, Brown
    
    for i, (avg_type, values) in enumerate(list(overall_data.items())[1:]):  # Skip accuracy for now
        bars = ax2.bar(x2 + i*width2, values, width2, label=avg_type, color=colors2[i], alpha=0.8)
        
        # Add value labels on bars
        for bar, val in zip(bars, values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{val:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Add accuracy as a horizontal line
    ax2.axhline(y=report['accuracy'], color='red', linestyle='--', linewidth=2, 
                label=f'Overall Accuracy ({report["accuracy"]:.3f})')
    
    ax2.set_xlabel('Metric', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax2.set_title('Overall Performance Metrics', fontsize=13, fontweight='bold')
    ax2.set_xticks(x2 + width2/2)
    ax2.set_xticklabels([m.title() for m in metrics])
    ax2.legend()
    ax2.set_ylim(0, 1.1)
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('figures/classification_report.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Classification report saved as 'figures/classification_report.png'")

def create_confidence_analysis(confidences, labels, predictions, class_names):
    """
    Create confidence distribution analysis (bonus figure)
    """
    plt.figure(figsize=(12, 4))
    
    # Convert to numpy arrays
    confidences = np.array(confidences)
    labels = np.array(labels)
    predictions = np.array(predictions)
    
    # Create subplots for confidence analysis
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    # Plot 1: Overall confidence distribution
    axes[0].hist(confidences, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    axes[0].set_xlabel('Prediction Confidence')
    axes[0].set_ylabel('Frequency')
    axes[0].set_title('Distribution of Prediction Confidence Scores')
    axes[0].grid(alpha=0.3)
    
    # Plot 2: Confidence by correctness
    correct_mask = labels == predictions
    correct_conf = confidences[correct_mask]
    incorrect_conf = confidences[~correct_mask]
    
    axes[1].hist([correct_conf, incorrect_conf], bins=20, alpha=0.7, 
                label=['Correct', 'Incorrect'], color=['green', 'red'])
    axes[1].set_xlabel('Prediction Confidence')
    axes[1].set_ylabel('Frequency')
    axes[1].set_title('Confidence Distribution by Prediction Correctness')
    axes[1].legend()
    axes[1].grid(alpha=0.3)
    
    # Plot 3: Confidence by class
    for i, class_name in enumerate(class_names):
        class_mask = predictions == i
        class_conf = confidences[class_mask]
        axes[2].hist(class_conf, bins=15, alpha=0.6, label=class_name)
    
    axes[2].set_xlabel('Prediction Confidence')
    axes[2].set_ylabel('Frequency')
    axes[2].set_title('Confidence Distribution by Predicted Class')
    axes[2].legend()
    axes[2].grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('figures/confidence_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Confidence analysis saved as 'figures/confidence_analysis.png'")
    
    # Print confidence statistics
    print(f"\nConfidence Statistics:")
    print(f"Mean confidence: {np.mean(confidences):.4f}")
    print(f"Std confidence: {np.std(confidences):.4f}")
    print(f"Mean confidence (correct predictions): {np.mean(correct_conf):.4f}")
    print(f"Mean confidence (incorrect predictions): {np.mean(incorrect_conf):.4f}")

def main():
    """
    Main function to run evaluation and generate figures
    """
    # Create figures directory if it doesn't exist
    import os
    os.makedirs('figures', exist_ok=True)
    
    # Load datasets
    _, _, test_dataset = get_datasets()
    test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)

    # Load model
    model = create_model(NUM_CLASSES, DEVICE)
    model.load_state_dict(torch.load("models/densenet_tb_pneumonia.pt", map_location=DEVICE))
    model.to(DEVICE)

    # Evaluate and generate figures
    print("Evaluating model and generating figures...")
    report, cm, confidences = evaluate_test(model, test_loader, save_figures=True)
    
    print("\nEvaluation complete! Figures saved in 'figures/' directory.")
    print("Generated files:")
    print("- figures/confusion_matrix.png")
    print("- figures/classification_report.png") 
    print("- figures/confidence_analysis.png (bonus)")

if __name__ == "__main__":
    main()