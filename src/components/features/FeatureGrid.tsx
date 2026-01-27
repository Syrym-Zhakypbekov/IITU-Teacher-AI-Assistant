import React from 'react';
import { motion } from 'framer-motion';

export interface Feature {
  title: string;
  description: string;
  icon?: React.ReactNode;
}

interface FeatureGridProps {
  features: Feature[];
}

export const FeatureGrid: React.FC<FeatureGridProps> = ({ features }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
      {features.map((feature, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: index * 0.1 }}
          className="p-8 bg-white dark:bg-slate-900 rounded-[2rem] border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-2xl transition-all group"
        >
          <div className="w-14 h-14 bg-blue-50 dark:bg-blue-900/30 rounded-2xl flex items-center justify-center text-blue-600 mb-6 group-hover:scale-110 group-hover:rotate-3 transition-transform">
            {feature.icon}
          </div>
          <h3 className="text-xl font-black text-slate-900 dark:text-white mb-3">
            {feature.title}
          </h3>
          <p className="text-slate-500 dark:text-slate-400 font-medium leading-relaxed">
            {feature.description}
          </p>
        </motion.div>
      ))}
    </div>
  );
};
