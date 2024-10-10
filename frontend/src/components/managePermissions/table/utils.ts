import { hashRouter } from "@/router";
import { selectedApplicationId } from "@/store/ApplicationState";

export const navigateToUserDetails = (userId: string) => {
    hashRouter.push({
        name: "UserDetails",
        params: {
            applicationId: selectedApplicationId.value,
            userId,
        },
    });
};
