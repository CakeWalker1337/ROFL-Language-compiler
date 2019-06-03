

define i32 @func.f1(i32 %a) {
    %a.ptr = alloca i32
    store i32 %a, i32* %a.ptr
    %a.1 = load i32, i32* %a.ptr
    %buffer3 = getelementptr inbounds [4 x i8], [4 x i8]* @.str.1, i32 0, i32 0 
    call i32 (i8*, ...) @printf(i8* %buffer3, i32 %a.1)
    %a.4 = load i32, i32* %a.ptr
    %buffer5 = icmp slt i32 %a.4, 5
    br i1 %buffer5, label %lab.0, label %lab.1
lab.0:
    %a.6 = load i32, i32* %a.ptr
    %a.7 = load i32, i32* %a.ptr
    %buffer8 = add i32 %a.7, 1
    %f1.9 = call i32 @func.f1(i32 %buffer8)
    %buffer10 = add i32 %a.6, %f1.9
    ret i32 %buffer10
    br label %lab.2
lab.1:
    br label %lab.2
lab.2:
    ret i32 5
}

define i32 @main() {
    %f1.11 = call i32 @func.f1(i32 1)
    ret i32 0
}

declare i32 @printf(i8*, ...)
@.str.1 = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
