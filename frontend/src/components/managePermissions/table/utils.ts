import { hashRouter } from "@/router";
import { routeItems } from "@/router/RouteItem";
import { selectedApplicationId } from "@/store/ApplicationState";

export const navigateToUserDetails = (userId: string) => {
    hashRouter.push({
        name: routeItems.userDetails.name,
        params: {
            applicationId: selectedApplicationId.value,
            userId,
        },
    });
};
