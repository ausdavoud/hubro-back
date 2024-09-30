type productKeyType = "basic" | "sporty" | "green" | "safe" | "production";

type RnDProjectType = {
  title: string;
  developmentCost: number;
  developmentDuration: number;
  isUnlocked: boolean;
  key: productKeyType;
};

type UpgradeType = RnDProjectType & {
  unitMatCostEffect: number | null;
  productionEmissionEffect: number | null;
};

type ProductType = RnDProjectType & {
  originalMatCost: number;
  timeSpent: number;
};

type Get_RnDProjects = {
  upgrades: Array<UpgradeType>;
  products: Array<ProductType>;
};
