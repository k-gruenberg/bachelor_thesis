import Data.List
import Data.Char

trigrams word =
    map (map toLower) [take 3 . drop i $ word| i <- [0..length word - 3]]

similarity attrName1 attrName2 =
    (fromIntegral $ length aIntersectB) / (fromIntegral $ length aUnionB)
    where a = nub $ trigrams attrName1
          b = nub $ trigrams attrName2
          aIntersectB = a `intersect` b
          aUnionB     = a `union`     b