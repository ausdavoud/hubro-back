type productKeyType = "basic" | "sporty" | "green" | "safe";

type RnDProjectType = {
  title: string;
  developmentCost: number;
  developmentDuration: number;
  isUnlocked: boolean;
};

type UpgradeType = RnDProjectType & {
  unitMatCostEffect: number | null;
  productionEmissionEffect: number | null;
};

type ProductType = RnDProjectType & {
  originalMatCost: number;
  key: productKeyType;
  timeSpent: number;
};

type Get_RnDProjects = {
  upgrades: Array<UpgradeType>;
  products: Array<ProductType>;
};
