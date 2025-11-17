"""Data enrichment module for exercise-to-muscle group mapping."""
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple


class DataEnrichment:
    """Enrich workout data with muscle group mappings."""
    
    def __init__(self, mapping_config: Dict[str, Any]):
        """Initialize data enrichment with exercise mapping configuration.
        
        Args:
            mapping_config: Dictionary containing exercise mapping configuration
        """
        self.config = mapping_config
        self.unmapped_exercises: List[str] = []
        self.exercise_cache: Dict[str, Tuple[str, str]] = {}
        
        # Build exercise lookup dictionary for faster matching
        self._build_exercise_lookup()
    
    def _build_exercise_lookup(self):
        """Build a dictionary for fast exercise name lookup."""
        self.exercise_lookup: Dict[str, Tuple[str, str]] = {}
        
        exercises = self.config.get('exercises', [])
        for exercise_def in exercises:
            level1 = exercise_def['level1']
            level2 = exercise_def['level2']
            
            for name in exercise_def.get('names', []):
                # Store normalized name as key
                normalized = self._normalize_name(name)
                self.exercise_lookup[normalized] = (level1, level2)
    
    def _normalize_name(self, name: str) -> str:
        """Normalize exercise name for matching.
        
        Args:
            name: Exercise name to normalize
            
        Returns:
            Normalized name (lowercase, stripped, single spaces)
        """
        return ' '.join(name.lower().strip().split())
    
    def enrich_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enrich dataframe with muscle group columns.
        
        Args:
            df: DataFrame with workout data
            
        Returns:
            DataFrame with added muscle_group_level1 and muscle_group_level2 columns
        """
        self.unmapped_exercises = []
        
        if 'exercise_name' not in df.columns:
            raise ValueError("DataFrame must have 'exercise_name' column")
        
        # Apply mapping to each exercise
        muscle_mappings = df['exercise_name'].apply(self._map_exercise_to_muscles)
        
        # Split tuple into two columns
        df['muscle_group_level1'] = muscle_mappings.apply(lambda x: x[0])
        df['muscle_group_level2'] = muscle_mappings.apply(lambda x: x[1])
        
        return df
    
    def _map_exercise_to_muscles(self, exercise_name: str) -> Tuple[str, str]:
        """Map an exercise name to muscle groups.
        
        Args:
            exercise_name: Name of the exercise
            
        Returns:
            Tuple of (level1, level2) muscle groups
        """
        if pd.isna(exercise_name) or exercise_name == '':
            return ('unknown', 'unknown')
        
        # Check cache first
        if exercise_name in self.exercise_cache:
            return self.exercise_cache[exercise_name]
        
        normalized = self._normalize_name(str(exercise_name))
        
        # Try exact match
        result = self._exact_match(normalized)
        if result:
            self.exercise_cache[exercise_name] = result
            return result
        
        # Try fuzzy match
        result = self._fuzzy_match(normalized)
        if result:
            self.exercise_cache[exercise_name] = result
            return result
        
        # Apply default mapping
        result = self._apply_default_mapping()
        self.unmapped_exercises.append(exercise_name)
        self.exercise_cache[exercise_name] = result
        
        return result
    
    def _exact_match(self, normalized_name: str) -> Optional[Tuple[str, str]]:
        """Try exact match against configured exercises.
        
        Args:
            normalized_name: Normalized exercise name
            
        Returns:
            Tuple of (level1, level2) if match found, None otherwise
        """
        return self.exercise_lookup.get(normalized_name)
    
    def _fuzzy_match(self, normalized_name: str) -> Optional[Tuple[str, str]]:
        """Try fuzzy matching using keyword rules.
        
        Args:
            normalized_name: Normalized exercise name
            
        Returns:
            Tuple of (level1, level2) if match found, None otherwise
        """
        fuzzy_rules = self.config.get('fuzzy_rules', [])
        
        for rule in fuzzy_rules:
            keyword = rule['keyword'].lower()
            exclude = rule.get('exclude', [])
            
            # Check if keyword is in exercise name
            if keyword in normalized_name:
                # Check exclusions
                excluded = False
                for exclude_term in exclude:
                    if exclude_term.lower() in normalized_name:
                        excluded = True
                        break
                
                if not excluded:
                    return (rule['level1'], rule['level2'])
        
        return None
    
    def _apply_default_mapping(self) -> Tuple[str, str]:
        """Apply default mapping for unknown exercises.
        
        Returns:
            Tuple of (level1, level2) default mapping
        """
        default = self.config.get('default_mapping', {})
        return (
            default.get('level1', 'upper'),
            default.get('level2', 'unknown')
        )
    
    def get_unmapped_exercises(self) -> List[str]:
        """Get list of exercises that couldn't be mapped exactly.
        
        Returns:
            List of unmapped exercise names
        """
        # Return unique unmapped exercises
        return list(set(self.unmapped_exercises))
    
    def get_mapping_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get summary of muscle group mappings in the dataset.
        
        Args:
            df: Enriched DataFrame
            
        Returns:
            Dictionary with mapping statistics
        """
        if 'muscle_group_level1' not in df.columns:
            return {}
        
        summary = {
            'total_exercises': len(df),
            'unique_exercises': df['exercise_name'].nunique(),
            'unmapped_count': len(self.unmapped_exercises),
            'unmapped_exercises': self.get_unmapped_exercises(),
            'level1_distribution': df['muscle_group_level1'].value_counts().to_dict(),
            'level2_distribution': df['muscle_group_level2'].value_counts().to_dict()
        }
        
        return summary
    
    def suggest_mapping(self, exercise_name: str) -> List[Tuple[str, str, float]]:
        """Suggest possible muscle group mappings for an exercise.
        
        Args:
            exercise_name: Exercise name to suggest mappings for
            
        Returns:
            List of (level1, level2, confidence) tuples
        """
        suggestions = []
        normalized = self._normalize_name(exercise_name)
        
        # Check exact match first
        exact = self._exact_match(normalized)
        if exact:
            suggestions.append((exact[0], exact[1], 1.0))
            return suggestions
        
        # Check fuzzy matches
        fuzzy = self._fuzzy_match(normalized)
        if fuzzy:
            suggestions.append((fuzzy[0], fuzzy[1], 0.7))
        
        # Add default as lowest confidence
        default = self._apply_default_mapping()
        suggestions.append((default[0], default[1], 0.3))
        
        return suggestions
